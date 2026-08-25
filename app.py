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

# Estilo Personalizado CSS para Tags Compactas
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .tag-badge {
        display: inline-block;
        background-color: #E2E8F0;
        color: #1E293B;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 2px;
    }
    .tag-valor {
        display: inline-block;
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    .tag-data {
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<div class='main-title'>🤖 DocAgent Pipeline</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Central Inteligente de Leitura, Classificação e Análise de Documentos com Inteligência Artificial</div>", unsafe_allow_html=True)

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
    st.markdown("### 🔌 Conexão do Sistema")
    if api_online:
        st.success("Status: Sistema Online 🟢")
    else:
        st.error("Status: Desconectado 🔴")
        
    st.markdown("---")
    st.markdown("### 💡 Como Usar?")
    st.markdown("""
    1. **Enviar:** Suba seu PDF ou texto na aba 1.
    2. **Processar:** Peça para a IA analisar na aba 2.
    3. **Insights:** Veja o painel executivo e gráficos na aba 3!
    """)
    st.caption("Portfólio de Engenharia de Software Sênior.")

if not api_online:
    st.warning("⚠️ O backend não está respondendo. Verifique os containers.")

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
    "📥 1. Enviar Documento", 
    "⚙️ 2. Processar com IA", 
    "📊 3. Dashboard Executivo & Gráficos"
])

# ABA 1: INGESTÃO
with tab_add:
    st.subheader("Envio de Novos Documentos para Análise")
    st.info("💡 Envie arquivos em **PDF, TXT ou MD**. A IA fará a extração do texto automaticamente.")
    
    if "input_titulo" not in st.session_state:
        st.session_state.input_titulo = ""
    if "input_conteudo" not in st.session_state:
        st.session_state.input_conteudo = ""

    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col2:
        st.markdown("##### 📁 Selecionar Arquivo")
        arquivo_enviado = st.file_uploader("Escolha o documento PDF ou texto", type=["txt", "md", "pdf"])
        
        if arquivo_enviado is not None:
            texto_extraido = ""
            try:
                if arquivo_enviado.name.endswith('.pdf'):
                    import pypdf
                    reader = pypdf.PdfReader(arquivo_enviado)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            texto_extraido += extracted + "\n"
                else:
                    texto_extraido = arquivo_enviado.read().decode("utf-8")
                
                if texto_extraido:
                    st.session_state.input_titulo = arquivo_enviado.name.rsplit('.', 1)[0].replace("_", " ").title()
                    st.session_state.input_conteudo = texto_extraido
                    st.success(f"✅ Arquivo '{arquivo_enviado.name}' lido com sucesso!")
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {str(e)}")

    with col1:
        st.markdown("##### 📝 Detalhes do Documento")
        novo_titulo = st.text_input("Título", value=st.session_state.input_titulo, placeholder="Ex: Relatório Master")
        novo_conteudo = st.text_area("Conteúdo Extraído", value=st.session_state.input_conteudo, placeholder="O texto aparecerá aqui...", height=200)

    if st.button("🚀 Enviar para Fila", type="primary"):
        if not api_online:
            st.error("Sistema offline.")
        elif not novo_titulo or not novo_conteudo:
            st.warning("Preencha o título e o conteúdo.")
        else:
            try:
                payload = {"titulo": novo_titulo, "conteudo": novo_conteudo}
                response = requests.post(f"{BACKEND_URL}/documentos", json=payload)
                if response.status_code == 201:
                    st.success("🎉 Documento enviado! Vá para a aba 'Processar com IA'.")
                    st.session_state.input_titulo = ""
                    st.session_state.input_conteudo = ""
                    st.rerun()
                else:
                    st.error(f"Erro: {response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")

# ABA 2: PIPELINE
with tab_pipeline:
    st.subheader("Processamento por Inteligência Artificial")
    
    if not documentos:
        st.warning("Nenhum documento cadastrado.")
    else:
        col_list, col_det = st.columns([2, 3], gap="medium")
        
        with col_list:
            st.markdown("##### 📂 Lista de Documentos")
            dados_tabela = []
            for d in documentos:
                status_emoji = "⏳ Na Fila"
                if d['status'] == "Processando": status_emoji = "🔄 Analisando"
                elif d['status'] == "Concluído": status_emoji = "✅ Concluído"
                elif d['status'] == "Erro": status_emoji = "❌ Erro"
                    
                dados_tabela.append({"ID": d['id'], "Título": d['titulo'], "Status": status_emoji})
            
            st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
            
            doc_ids = [d['id'] for d in documentos]
            doc_titulos = {d['id']: f"ID {d['id']} - {d['titulo']}" for d in documentos}
            selecionado_id = st.selectbox("Selecione para processar:", options=doc_ids, format_func=lambda x: doc_titulos[x])
            
        with col_det:
            doc_sel = next((d for d in documentos if d['id'] == selecionado_id), None)
            if doc_sel:
                st.markdown(f"### 🔍 {doc_sel['titulo']}")
                st.write(f"**Status:** {doc_sel['status']}")
                
                pode_processar = doc_sel['status'] in ["Pendente", "Erro"]
                if pode_processar:
                    if st.button("✨ Executar Análise com IA", type="primary", use_container_width=True):
                        with st.spinner("A IA está interpretando o documento..."):
                            try:
                                proc_res = requests.post(f"{BACKEND_URL}/documentos/{doc_sel['id']}/processar")
                                if proc_res.status_code == 200:
                                    st.success("🎉 Análise concluída com sucesso!")
                                    st.rerun()
                                else:
                                    st.error(f"Erro: {proc_res.json().get('detail', 'Erro')}")
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")
                else:
                    st.success("✅ Documento já processado.")

# ABA 3: DASHBOARD EXECUTIVO & GRÁFICOS EM PIZZA/ROSCA (PLOTLY)
with tab_dashboard:
    st.subheader("📊 Dashboard Executivo & Gráficos Analíticos")
    
    if not documentos:
        st.info("Aguardando documentos para gerar os gráficos.")
    else:
        totais = len(documentos)
        concluidos = sum(1 for d in documentos if d['status'] == "Concluído")
        pendentes = sum(1 for d in documentos if d['status'] == "Pendente")
        erros = sum(1 for d in documentos if d['status'] == "Erro")
        
        # Métricas no Topo
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total de Documentos", totais)
        m2.metric("Sucesso da IA", concluidos)
        m3.metric("Pendentes", pendentes)
        m4.metric("Erros", erros)
        
        st.markdown("---")
        
        # Gráficos Profissionais em Pizza/Rosca com Plotly
        try:
            import plotly.express as px
            
            col_g1, col_g2 = st.columns(2, gap="medium")
            
            with col_g1:
                st.markdown("##### 🍩 Distribuição de Status do Pipeline")
                df_status = pd.DataFrame({
                    "Status": ["Concluído", "Pendente", "Erros"],
                    "Quantidade": [concluidos, pendentes, erros]
                })
                fig_status = px.pie(df_status, names="Status", values="Quantidade", hole=0.4, 
                                    color_discrete_sequence=["#10B981", "#F59E0B", "#EF4444"])
                fig_status.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260)
                st.plotly_chart(fig_status, use_container_width=True)
                
            with col_g2:
                st.markdown("##### 📊 Tipos de Documentos Identificados")
                tipos_lista = []
                for d in documentos:
                    ext = d.get('extracao_dados')
                    if isinstance(ext, dict):
                        tipos_lista.append(ext.get('tipo_documento', 'Não classificado'))
                    else:
                        tipos_lista.append('Não Processado')
                
                df_tipos = pd.DataFrame(tipos_lista, columns=["Tipo"]).value_counts().reset_index(name="Total")
                fig_tipos = px.bar(df_tipos, x="Tipo", y="Total", text="Total", 
                                   color="Tipo", color_discrete_sequence=px.colors.qualitative.Prism)
                fig_tipos.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260, showlegend=False)
                st.plotly_chart(fig_tipos, use_container_width=True)
                
        except ImportError:
            st.warning("Biblioteca Plotly não encontrada.")

        st.markdown("---")
        st.markdown("### 📋 Resumo Inteligente por Documento")
        
        # Função auxiliar interna para limpar quebras de linha e espaços múltiplos das strings do JSON
        def limpar_texto(texto):
            if not texto:
                return ""
            # Substitui qualquer quebra de linha ou espaço excessivo por um espaço simples
            return " ".join(str(texto).split())

        # Cards Compactos e Organizados com Tratamento de Dados Blindado
        for d in documentos:
            ext = d.get('extracao_dados')
            with st.container(border=True):
                col_h1, col_h2 = st.columns([3, 1])
                with col_h1:
                    st.markdown(f"#### 📄 {d['titulo']}")
                with col_h2:
                    st.markdown(f"**Status:** `{d['status']}`")
                
                if isinstance(ext, dict):
                    st.markdown("---")
                    
                    col_meta1, col_meta2, col_meta3 = st.columns(3, gap="medium")
                    
                    with col_meta1:
                        st.markdown(f"**🏷️ Classificação:**\n`{ext.get('tipo_documento', 'N/A')}`")
                        entidades = ext.get('entidades_mencionadas', [])
                        if isinstance(entidades, list) and entidades:
                            ent_limpas = [limpar_texto(e) for e in entidades if limpar_texto(e)]
                            ent_str = ", ".join(ent_limpas) if ent_limpas else "Nenhuma"
                        else:
                            ent_str = "Nenhuma"
                        st.markdown(f"**🏢 Entidades:**\n{ent_str}")
                            
                    with col_meta2:
                        datas = ext.get('datas', [])
                        if isinstance(datas, list) and datas:
                            # Junta as datas limpando as quebras de linha internas e separando por pipe (|)
                            datas_limpas = [limpar_texto(dt) for dt in datas if limpar_texto(dt)]
                            datas_str = " | ".join(datas_limpas) if datas_limpas else "Nenhuma"
                        else:
                            datas_str = "Nenhuma"
                        st.markdown(f"**📅 Datas:**\n{datas_str}")
                            
                    with col_meta3:
                        valores = ext.get('valores', [])
                        if isinstance(valores, list) and valores:
                            # Junta os valores limpando as quebras de linha internas (ex: R$ 35.00)
                            val_limpos = [limpar_texto(v) for v in valores if limpar_texto(v)]
                            val_str = ", ".join(val_limpos) if val_limpos else "Nenhum"
                        else:
                            val_str = "Nenhum"
                        st.markdown(f"**💰 Valores:**\n{val_str}")
                    
                    st.markdown("---")
                    st.markdown("**📌 Resumo Executivo da IA:**")
                    resumo_bruto = ext.get('resumo', 'Sem resumo disponível.')
                    resumo_limpo = limpar_texto(resumo_bruto)
                    st.info(resumo_limpo)
                else:
                    st.warning("⏳ Este documento ainda aguarda o processamento da inteligência artificial.")