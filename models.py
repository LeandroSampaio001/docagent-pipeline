from sqlalchemy import Column, Integer, String, Text
from database import Base

class DocumentoModel(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    conteudo = Column(Text)
    status = Column(String, default="Pendente")