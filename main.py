from fastapi import FastAPI

app = FastAPI(
    title="DocAgent Pipeline",
    description="API REST para pipeline de ingestão e análise de documentos",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao DocAgent Pipeline!"}