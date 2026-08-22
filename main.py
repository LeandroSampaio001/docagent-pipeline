from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
from models import DocumentoModel
from schemas import DocumentoCreate, DocumentoResponse
from gemini_service import analisar_documento_com_gemini

# Cria as tabelas no banco de dados na inicialização do app
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DocAgent Pipeline API",
    description="API REST de alta performance para ingestão, classificação e extração inteligente de documentos com Gemini 1.5",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "app": "DocAgent Pipeline API",
        "version": "1.0.0",
        "status": "Online",
        "documentation": "/docs"
    }

@app.post("/documentos", response_model=DocumentoResponse, status_code=status.HTTP_201_CREATED)
def criar_documento(doc: DocumentoCreate, db: Session = Depends(get_db)):
    """
    Cadastra um novo documento no pipeline com status 'Pendente'.
    """
    novo_doc = DocumentoModel(
        titulo=doc.titulo,
        conteudo=doc.conteudo,
        status="Pendente"
    )
    db.add(novo_doc)
    db.commit()
    db.refresh(novo_doc)
    return novo_doc

@app.get("/documentos", response_model=List[DocumentoResponse])
def listar_documentos(db: Session = Depends(get_db)):
    """
    Retorna a lista completa de documentos registrados.
    """
    return db.query(DocumentoModel).order_by(DocumentoModel.id.desc()).all()

@app.get("/documentos/{documento_id}", response_model=DocumentoResponse)
def obter_documento(documento_id: int, db: Session = Depends(get_db)):
    """
    Recupera os detalhes de um documento específico pelo ID.
    """
    doc = db.query(DocumentoModel).filter(DocumentoModel.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return doc

@app.post("/documentos/{documento_id}/processar", response_model=DocumentoResponse)
async def processar_documento(documento_id: int, db: Session = Depends(get_db)):
    """
    Dispara o processamento inteligente via IA para extração de metadados do documento.
    """
    doc = db.query(DocumentoModel).filter(DocumentoModel.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    if doc.status == "Processando":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este documento já está sendo processado."
        )

    # Atualiza o status para Processando
    doc.status = "Processando"
    db.commit()
    db.refresh(doc)
    
    try:
        # Executa a extração usando a IA do Gemini ou o Fallback Heurístico
        resultado_ia = await analisar_documento_com_gemini(doc.titulo, doc.conteudo)
        
        doc.extracao_dados = resultado_ia
        doc.status = "Concluído"
        db.commit()
        db.refresh(doc)
    except Exception as e:
        doc.status = "Erro"
        doc.extracao_dados = {"erro": str(e)}
        db.commit()
        db.refresh(doc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no processamento do pipeline: {str(e)}"
        )
        
    return doc
