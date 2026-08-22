import os
import json
import logging
import re
from typing import Dict, Any
import httpx

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def extrair_dados_via_heuristica(titulo: str, conteudo: str) -> Dict[str, Any]:
    """
    Algoritmo heurístico local de fallback de alto nível.
    Analisa padrões no texto do documento para simular e extrair metadados estruturados.
    """
    logger.info("Executando extração local baseada em heurísticas (Fallback).")
    
    # Heurística para Tipo de Documento
    conteudo_lower = conteudo.lower()
    titulo_lower = titulo.lower()
    
    tipo = "Outro"
    if any(p in conteudo_lower or p in titulo_lower for p in ["contrato", "prestação de serviços", "cláusula"]):
        tipo = "Contrato"
    elif any(p in conteudo_lower or p in titulo_lower for p in ["nota fiscal", "nf-e", "danfe", "fatura"]):
        tipo = "Nota Fiscal"
    elif any(p in conteudo_lower or p in titulo_lower for p in ["recibo", "pagamento", "quitado"]):
        tipo = "Recibo"
    elif any(p in conteudo_lower or p in titulo_lower for p in ["memorando", "comunicação interna", "ofício"]):
        tipo = "Memorando"
    elif any(p in conteudo_lower or p in titulo_lower for p in ["relatório", "report", "análise"]):
        tipo = "Relatório"

    # Heurística para Valores Monetários (R$, $, USD)
    valores = re.findall(r"(?:R\$\s*|USD\s*|\$\s*)\d+(?:[\.,]\d{2})?", conteudo)
    valores_limpos = list(set([v.strip() for v in valores]))

    # Heurística para Datas (DD/MM/AAAA ou DD de Mês de AAAA)
    datas = re.findall(r"\d{2}/\d{2}/\d{4}|\d{2}\s+de\s+[a-zA-Zçéíóú]+\s+de\s+\d{4}", conteudo, re.IGNORECASE)
    datas_limpas = list(set([d.strip() for d in datas]))

    # Heurística para Entidades (Empresas Ltda, S/A, ou Nomes Próprios Comuns em contratos)
    entidades = re.findall(r"([A-Z][a-zA-Z0-9À-ÖØ-öø-ÿ\s\.\-]+(?:Ltda|S\.A\.|S/A|Eireli|CNPJ))", conteudo)
    entidades_limpas = list(set([ent.strip() for ent in entidades]))

    # Heurística para Resumo
    frases = [f.strip() for f in conteudo.split(".") if len(f.strip()) > 10]
    resumo = ""
    if frases:
        resumo = frases[0] + "."
        if len(frases) > 1:
            resumo += " " + frases[1] + "."
    else:
        resumo = f"Este documento é um {tipo} intitulado '{titulo}' com conteúdo textual simplificado."

    return {
        "tipo_documento": tipo,
        "entidades_mencionadas": entidades_limpas[:5],
        "valores": valores_limpos[:5],
        "datas": datas_limpas[:5],
        "resumo": resumo,
        "metodo_extracao": "Local Heuristic (Fallback Mode)"
    }


async def analisar_documento_com_gemini(titulo: str, conteudo: str) -> Dict[str, Any]:
    """
    Envia o título e conteúdo do documento para o Gemini para fazer extração estruturada de dados.
    Caso a chave da API não exista ou a chamada falhe, utiliza o motor de heurística local.
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY não configurada. Usando fallback local.")
        return extrair_dados_via_heuristica(titulo, conteudo)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Você é um assistente especialista em análise de documentos e extração de dados.
    Analise o seguinte documento com o título "{titulo}" e o conteúdo abaixo:
    
    ---- INÍCIO DO CONTEÚDO ----
    {conteudo}
    ---- FIM DO CONTEÚDO ----
    
    Extraia exatamente os seguintes metadados em formato JSON estruturado:
    {{
        "tipo_documento": "Uma string classificando o tipo do documento (ex: Contrato, Nota Fiscal, Recibo, Memorando, Relatório, Outro)",
        "entidades_mencionadas": ["Uma lista com os principais nomes de pessoas físicas ou jurídicas mencionadas no documento"],
        "valores": ["Uma lista de valores monetários encontrados no texto (com o respectivo símbolo R$, $, etc.)"],
        "datas": ["Uma lista de datas identificadas no texto"],
        "resumo": "Um resumo executivo e conciso com no máximo 3 frases descrevendo do que se trata o documento"
    }}

    Retorne APENAS o JSON válido. Não adicione nenhuma formatação markdown extra de blocos como ```json ... ``` ou explicações.
    """

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            # Extrai o texto retornado pelo Gemini
            response_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Tenta decodificar o JSON diretamente
            extracao = json.loads(response_text.strip())
            extracao["metodo_extracao"] = "Google Gemini AI (1.5-flash)"
            logger.info("Extração via Gemini executada com sucesso!")
            return extracao
            
    except Exception as e:
        logger.error(f"Erro na extração via Gemini: {str(e)}. Executando fallback.")
        fallback = extrair_dados_via_heuristica(titulo, conteudo)
        fallback["erro_api"] = str(e)
        return fallback
