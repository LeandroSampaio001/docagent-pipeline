from sqlalchemy import Column, Integer, String, Text, JSON
from database import Base

class DocumentoModel(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    conteudo = Column(Text)
    status = Column(String, default="Pendente") # Pendente, Processando, Concluído, Erro
    extracao_dados = Column(JSON, nullable=True) # Dados estruturados extraídos pela IA
