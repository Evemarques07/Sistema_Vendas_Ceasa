#models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.enums import TipoUsuario

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    cpf_ou_cnpj = Column(String(18), unique=True, index=True, nullable=True)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(SQLEnum(TipoUsuario), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
