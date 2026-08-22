from pydantic import BaseModel
from typing import Optional, Dict, Any

class DocumentoBase(BaseModel):
    titulo: str
    conteudo: str

class DocumentoCreate(DocumentoBase):
    pass

class DocumentoResponse(DocumentoBase):
    id: int
    status: str
    extracao_dados: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
