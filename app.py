import streamlit as st
import requests
import os
import json
import pandas as pd
from datetime import datetime

# Configurações da Página
st.set_page_config(
    page_title="DocAgent Pipeline - IA Extratora",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração do Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Estilo Personalizado CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .status-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .status-pendente {
        background-color: #FEF3C7;
        color: #D97706;
        border: 1px solid #F59E0B;
    }
    .status-processando {
        background-color: #DBEAFE;
        color: #2563EB;
        border: 1px solid #3B82F6;
    }
    .status-concluido {
        background-color: #D1FAE5;
        color: #059669;
        border: 1px solid #10B981;
    }
    .status-erro {
        background-color: #FEE2E2;
        color: #DC2626;
        border: 1px solid #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# Título Principal da Aplicação
st.markdown("<div class='main-title'>🤖 DocAgent Pipeline</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Plataforma Inteligente de Classificação, Análise e Extração de Dados em Documentos com IA Gemini</div>", unsafe_allow_html=True)

# Verificação de Conexão com a API
api_online = False
try:
    response = requests.get(f"{BACKEND_URL}/")
    if response.status_code == 200:
        api_online = True
except Exception:
    api_online = False

# Sidebar
with st.sidebar:
    st.markdown("### 🔌 Conexão da API")
    if api_online:
        st.success("API: Conectada")
    else:
        st.error("API: Desconectada")
        st.info(f"Tentando conectar em: {BACKEND_URL}")
        
    st.markdown("---")
    st.markdown("### ℹ️ Sobre o Portfólio")
    st.markdown("""
    Este sistema representa um pipeline moderno de processamento de documentos não estruturados.
    
    **Tecnologias Utilizadas:**
    - **FastAPI** (Backend RESTful)
    - **SQLAlchemy** & **PostgreSQL**
    - **Google Gemini 1.5 Flash API**
    - **Streamlit** (Frontend Reativo)
    - **Docker & Docker Compose**
    """)
    st.caption("Desenvolvido para Portfólio de Engenharia de Software Sênior.")

# Se a API estiver offline, exibe aviso e interrompe fluxo de dados do backend, mas mantém a UI viva
if not api_online:
    st.warning("⚠️ O backend (FastAPI) não parece estar respondendo. Por favor, verifique se os containers estão rodando com `docker-compose up`.")

# Puxar todos os documentos do banco de dados (função padrão sem o fragment)
def get_documentos():
    try:
        res = requests.get(f"{BACKEND_URL}/documentos")
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

documentos = get_documentos() if api_online else []

# Criação das Abas da Aplicação
tab_add, tab_pipeline, tab_dashboard = st.tabs([
    "📥 Ingestão de Documento", 
    "⚙️ Pipeline & Processamento", 
    "📊 Dashboard & Metadados"
])

# ABA 1: INGESTÃO DE NOVO DOCUMENTO
with tab_add:
    st.subheader("Fazer Upload ou Cadastrar Novo Documento")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("##### Digitar ou Colar Texto")
        novo_titulo = st.text_input("Título do Documento", placeholder="Ex: Contrato de Prestação de Serviços - TI")
        novo_conteudo = st.text_area("Conteúdo Textual", placeholder="Cole o texto ou cláusulas do documento aqui...", height=250)
        
    with col2:
        st.markdown("##### Enviar Arquivo")
        arquivo_enviado = st.file_uploader("Selecione um arquivo de texto (.txt ou .md)", type=["txt", "md"])
        if arquivo_enviado is not None:
            # Substitui os valores se um arquivo for carregado
            texto_arquivo = arquivo_enviado.read().decode("utf-8")
            novo_titulo = arquivo_enviado.name.rsplit('.', 1)[0].replace("_", " ").title()
            novo_conteudo = texto_arquivo
            st.success(f"Arquivo '{arquivo_enviado.name}' carregado com sucesso!")
            st.text_area("Conteúdo do arquivo (prévia):", value=texto_arquivo[:500] + ("..." if len(texto_arquivo) > 500 else ""), height=120, disabled=True)

    # Botão de Envio
    if st.button("Enviar para Ingestão", type="primary"):
        if not api_online:
            st.error("Não é possível enviar. O backend está offline.")
        elif not novo_titulo or not novo_conteudo:
            st.warning("Por favor, informe o Título e o Conteúdo do documento.")
        else:
            try:
                payload = {"titulo": novo_titulo, "conteudo": novo_conteudo}
                response = requests.post(f"{BACKEND_URL}/documentos", json=payload)
                if response.status_code == 201:
                    st.success(f"Documento '{novo_titulo}' enviado ao pipeline com status 'Pendente'!")
                    st.rerun()
                else:
                    st.error(f"Falha ao salvar: {response.text}")
            except Exception as e:
                st.error(f"Erro ao conectar com a API: {str(e)}")

# ABA 2: PIPELINE & PROCESSAMENTO
with tab_pipeline:
    st.subheader("Gerenciar Pipeline de IA")
    
    if not documentos:
        st.info("Nenhum documento cadastrado no banco de dados. Vá para a aba 'Ingestão de Documento' para cadastrar.")
    else:
        col_list, col_det = st.columns([2, 3])
        
        with col_list:
            st.markdown("##### Lista de Documentos")
            
            # Formatar dados para exibição na tabela simplificada
            dados_tabela = []
            for d in documentos:
                status_emoji = "⏳"
                if d['status'] == "Processando":
                    status_emoji = "🔄"
                elif d['status'] == "Concluído":
                    status_emoji = "✅"
                elif d['status'] == "Erro":
                    status_emoji = "❌"
                    
                dados_tabela.append({
                    "ID": d['id'],
                    "Título": d['titulo'],
                    "Status": f"{status_emoji} {d['status']}"
                })
            
            df_docs = pd.DataFrame(dados_tabela)
            st.dataframe(df_docs, use_container_width=True, hide_index=True)
            
            # Seletor de documento para detalhamento
            doc_ids = [d['id'] for d in documentos]
            doc_titulos = {d['id']: f"ID {d['id']} - {d['titulo']}" for d in documentos}
            
            selecionado_id = st.selectbox(
                "Selecione um documento para detalhar ou processar:",
                options=doc_ids,
                format_func=lambda x: doc_titulos[x]
            )
            
        with col_det:
            # Recupera os dados completos do selecionado
            doc_sel = next((d for d in documentos if d['id'] == selecionado_id), None)
            
            if doc_sel:
                st.markdown(f"### Detalhes do Documento: {doc_sel['titulo']}")
                
                # Exibição de Status customizado com HTML
                st_class = f"status-{doc_sel['status'].lower()}"
                st.markdown(f"**Status atual:** <span class='status-badge {st_class}'>{doc_sel['status'].upper()}</span>", unsafe_allow_html=True)
                st.write("")
                
                # Ações
                col_btn, col_msg = st.columns([1, 1.5])
                with col_btn:
                    pode_processar = doc_sel['status'] in ["Pendente", "Erro"]
                    if st.button("🚀 Executar Pipeline de IA", disabled=not pode_processar, use_container_width=True, type="primary"):
                        with st.spinner("Enviando para a API e processando com Gemini..."):
                            try:
                                proc_res = requests.post(f"{BACKEND_URL}/documentos/{doc_sel['id']}/processar")
                                if proc_res.status_code == 200:
                                    st.success("Documento processado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error(f"Erro no processamento: {proc_res.json().get('detail', 'Erro desconhecido')}")
                            except Exception as e:
                                st.error(f"Erro ao chamar API: {str(e)}")
                                
                with col_msg:
                    if not pode_processar:
                        st.info("Este documento já foi processado ou está em andamento.")
                    else:
                        st.caption("Disparará a análise LLM estruturada no conteúdo textual.")
                
                st.markdown("---")
                
                # Abas internas de detalhes
                tab_det_text, tab_det_extracted = st.tabs(["📄 Conteúdo Original", "🔍 Dados Extraídos pela IA"])
                
                with tab_det_text:
                    st.text_area("Texto do Documento", value=doc_sel['conteudo'], height=200, disabled=True)
                    
                with tab_det_extracted:
                    ext = doc_sel.get('extracao_dados')
                    if not ext:
                        st.warning("Nenhum dado extraído ainda. Execute o Pipeline de IA para analisar este documento.")
                    else:
                        st.markdown(f"**Método de Extração:** `{ext.get('metodo_extracao', 'Desconhecido')}`")
                        
                        col_ext1, col_ext2 = st.columns([1, 1])
                        with col_ext1:
                            st.write("**Tipo do Documento:**")
                            st.info(ext.get('tipo_documento', 'Não classificado'))
                            
                            st.write("**Entidades Mencionadas:**")
                            entidades = ext.get('entidades_mencionadas', [])
                            if entidades:
                                for ent in entidades:
                                    st.markdown(f"- {ent}")
                            else:
                                st.caption("Nenhuma entidade detectada")
                                
                        with col_ext2:
                            st.write("**Datas Identificadas:**")
                            datas = ext.get('datas', [])
                            if datas:
                                for dat in datas:
                                    st.markdown(f"- {dat}")
                            else:
                                st.caption("Nenhuma data detectada")
                                
                            st.write("**Valores Encontrados:**")
                            valores = ext.get('valores', [])
                            if valores:
                                for val in valores:
                                    st.markdown(f"- `{val}`")
                            else:
                                st.caption("Nenhum valor detectado")
                                
                        st.write("**Resumo Executivo da IA:**")
                        st.success(ext.get('resumo', 'Sem resumo disponível.'))
                        
                        with st.expander("Ver Payload JSON Completo"):
                            st.json(ext)

# ABA 3: DASHBOARD & METADADOS
with tab_dashboard:
    st.subheader("Visão Geral e Métricas do Pipeline")
    
    if not documentos:
        st.info("Aguardando dados para consolidar estatísticas.")
    else:
        # Métricas de Alta Performance
        totais = len(documentos)
        concluidos = sum(1 for d in documentos if d['status'] == "Concluído")
        pendentes = sum(1 for d in documentos if d['status'] == "Pendente")
        erros = sum(1 for d in documentos if d['status'] == "Erro")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total de Documentos", totais)
        m2.metric("Processados com Sucesso", concluidos, f"{concluidos/totais*100:.1f}%" if totais > 0 else "0%")
        m3.metric("Fila de Espera (Pendente)", pendentes)
        m4.metric("Falhas no Pipeline", erros)
        
        st.markdown("---")
        st.markdown("### Visão Geral de Dados Consolidados")
        
        # Consolidação de uma tabela analítica com dados de extração
        linhas_analise = []
        for d in documentos:
            ext = d.get('extracao_dados') or {}
            linhas_analise.append({
                "ID": d['id'],
                "Título": d['titulo'],
                "Status": d['status'],
                "Tipo de Documento": ext.get('tipo_documento', 'N/A'),
                "Resumo": ext.get('resumo', 'N/A'),
                "Método de Extração": ext.get('metodo_extracao', 'N/A')
            })
            
        df_analise = pd.DataFrame(linhas_analise)
        st.dataframe(df_analise, use_container_width=True, hide_index=True)
