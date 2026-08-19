from fastapi import FastAPI
from database import engine
import models

# Cria as tabelas no banco de dados automaticamente ao iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocAgent Pipeline")

@app.get("/")
def home():
    return {"message": "API rodando e conectada ao PostgreSQL com sucesso!"}