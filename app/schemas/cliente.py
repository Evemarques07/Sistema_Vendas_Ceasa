from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schemas base para Cliente
class ClienteBase(BaseModel):
    nome: str
    nome_fantasia: Optional[str] = None
    cpf_ou_cnpj: str
    endereco: str
    ponto_referencia: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone1: str
    telefone2: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cpf_ou_cnpj: Optional[str] = None
    endereco: Optional[str] = None
    ponto_referencia: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone1: Optional[str] = None
    telefone2: Optional[str] = None
    ativo: Optional[bool] = None

class Cliente(ClienteBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True
