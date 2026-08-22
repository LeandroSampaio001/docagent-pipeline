# 🤖 DocAgent Pipeline

API REST de alta performance integrada com a LLM **Google Gemini 1.5 Flash** para ingestão, classificação e extração inteligente de metadados em documentos estruturados e não estruturados, acoplada a um painel analítico dinâmico em **Streamlit**.

---

## 🚀 Arquitetura do Sistema

O **DocAgent Pipeline** foi projetado seguindo princípios de arquitetura limpa, separação de responsabilidades e resiliência de serviços.

```
       [ Usuário / Navegador ]
                  │
                  ▼ (Porta 8501)
         [ Streamlit App ]
                  │
                  ▼ (HTTP/REST - Porta 8000)
         [ FastAPI Backend ]
           /      │      \
          /       │       \
         ▼        ▼        ▼
  [PostgreSQL] [Gemini AI] [Fallback Heurístico]
  (Porta 5432)  (Cloud LLM)    (Motor Regex Local)
```

1. **Frontend (Streamlit)**: Interface moderna e fluida para upload de arquivos, visualização do status da fila de ingestão, visualização de metadados extraídos pela inteligência artificial e acompanhamento de métricas analíticas.
2. **Backend (FastAPI)**: API REST assíncrona responsável pelo CRUD de documentos, controle de estados do pipeline (`Pendente` -> `Processando` -> `Concluído` / `Erro`) e orquestração de chamadas de IA.
3. **Banco de Dados (PostgreSQL)**: Persistência robusta com mapeamento objeto-relacional (ORM) via **SQLAlchemy**, armazenando o conteúdo bruto e as estruturas de metadados em colunas nativas do tipo `JSON`.
4. **Motor de IA (Google Gemini 1.5 Flash)**: Extração estruturada forçada via `responseMimeType: "application/json"`, recuperando em tempo recorde tipos de documentos, entidades chaves, valores monetários, datas e resumos.
5. **Resiliência (Fallback Heurístico)**: Se o serviço da Gemini falhar ou se nenhuma chave de API (`GEMINI_API_KEY`) estiver presente, a aplicação executa um motor heurístico regex sofisticado localmente, retornando dados simulados precisos e mantendo o fluxo 100% operacional.

---

## �️ Tecnologias de Ponta Utilizadas

* **Linguagem**: Python 3.10+
* **Backend**: FastAPI, Uvicorn, Pydantic v2
* **Persistência & ORM**: SQLAlchemy, Psycopg2, PostgreSQL 15-Alpine
* **Integração com LLM**: Google Gemini API via `httpx` assíncrono
* **Frontend**: Streamlit, Pandas
* **DevOps**: Docker, Docker Compose

---

## 📁 Estrutura do Projeto

```
docagent-pipeline/
├── app.py                # Interface visual Streamlit (Frontend)
├── main.py               # Configurações de rotas e inicialização do FastAPI
├── models.py             # Modelos declarativos do SQLAlchemy
├── database.py           # Conexão física e gerência de conexões (Sessions) do PostgreSQL
├── schemas.py            # Modelos de validação de dados Pydantic
├── gemini_service.py     # Lógica de integração com a LLM Gemini e Motor de Fallback
├── Dockerfile            # Configuração unificada de build Docker (multi-target runtime)
├── docker-compose.yml    # Orquestração local de containers de BD, API e UI
├── requirements.txt      # Gerenciamento de dependências Python
└── README.md             # Documentação técnica do projeto
```

---

## ⚙️ Como Executar o Projeto com Docker

### Pré-requisitos
* **Docker** e **Docker Compose** instalados na máquina de desenvolvimento.
* (Opcional) Uma chave de API do Gemini obtida gratuitamente no [Google AI Studio](https://aistudio.google.com/).

### Passo a Passo

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/LeandroSampaio001/docagent-pipeline.git
   cd docagent-pipeline
   ```

2. **Configurar a Chave da Gemini (Opcional):**
   * Você pode exportar a variável de ambiente direto no seu terminal:
     * **No Windows (PowerShell):**
       ```powershell
       $env:GEMINI_API_KEY="sua-chave-api-aqui"
       ```
     * **No Linux/macOS:**
       ```bash
       export GEMINI_API_KEY="sua-chave-api-aqui"
       ```
   * *Nota: Se você omitir este passo, a aplicação iniciará em **Modo Fallback Heurístico**, extraindo os metadados localmente sem quebrar o sistema!*

3. **Subir os Containers:**
   Execute o seguinte comando para buildar e iniciar todos os serviços de uma só vez:
   ```bash
   docker-compose up --build
   ```

4. **Acessar as Aplicações:**
   * **Interface Visual (Streamlit)**: [http://localhost:8501](http://localhost:8501)
   * **Documentação Swagger (FastAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Endpoint Raiz da API**: [http://localhost:8000/](http://localhost:8000/)

---

## � Detalhamento dos Endpoints da API (RESTful)

### 1. Ingestão de Documento
* **POST `/documentos`**
  * **Payload:**
    ```json
    {
      "titulo": "Contrato de Parceria Comercial - Empresa X",
      "conteudo": "Este contrato estabelece uma parceria de TI entre a TechLtda no valor de R$ 50.000,00 assinado em 22/08/2026."
    }
    ```
  * **Retorno (210 Created):** Retorna o documento salvo com status `"Pendente"`.

### 2. Listar Todos os Documentos
* **GET `/documentos`**
  * **Retorno:** Retorna um array com todos os documentos salvos, ordenados pelo mais recente.

### 3. Detalhes do Documento
* **GET `/documentos/{id}`**
  * **Retorno:** Detalhes de um único documento ou erro 404 se não encontrado.

### 4. Disparar Pipeline de IA
* **POST `/documentos/{id}/processar`**
  * **Funcionamento:** Muda o status para `"Processando"`, chama o serviço Gemini e realiza a extração do JSON com metadados estruturados. Ao final, altera o status para `"Concluído"`. Se falhar, altera para `"Erro"`.

---

## 💡 Recursos de Portfólio de Alto Nível Demonstrados

* **Design Pattern Fallback**: Mecanismo inteligente que substitui a API externa em caso de falha de conexão ou ausência de credenciais, ideal para testes locais ágeis.
* **Validação Robusta**: Conversão e filtragem de modelos do Pydantic para SQLAlchemy protegendo as camadas do banco de dados de payloads indesejados.
* **Armazenamento Não Estruturado em Banco de Dados Relacional**: Uso inteligente de tipo `JSON` nativo no PostgreSQL para manter alta flexibilidade de dados gerados por IA sem a rigidez de colunas pré-definidas.
* **Multi-stage Compose**: Uso reativo da mesma imagem base Docker para rodar diferentes entrypoints (FastAPI e Streamlit), reduzindo o desperdício de recursos e garantindo ambientes idênticos.
