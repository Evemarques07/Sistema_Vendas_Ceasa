from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoUsuario(str, Enum):
    ADMINISTRADOR = "administrador"
    FUNCIONARIO = "funcionario"

# Schemas para autenticação
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Login(BaseModel):
    login: str  # Pode ser email ou cpf/cnpj
    senha: str

# Schemas base para Usuario
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    cpf_ou_cnpj: str
    tipo: TipoUsuario

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf_ou_cnpj: Optional[str] = None
    tipo: Optional[TipoUsuario] = None
    ativo: Optional[bool] = None

class Usuario(UsuarioBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema para resposta de login
class LoginResponse(BaseModel):
    user: Usuario
    token: str
