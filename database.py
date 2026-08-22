import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o PostgreSQL (lê da variável de ambiente ou usa fallback local)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgrespassword@localhost:5432/docagent_db"
)

# O 'engine' gerencia a conexão física com o banco
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Fábrica de sessões para conversarmos com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criarmos nossos modelos de tabelas
Base = declarative_base()

# Dependência para abrir e fechar a sessão do banco em cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
