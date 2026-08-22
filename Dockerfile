FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema operacional necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código-fonte para o container
COPY . .

# Expõe as portas padrão de desenvolvimento
EXPOSE 8000
EXPOSE 8501

# Por padrão, inicia o uvicorn (pode ser sobrescrito no compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
