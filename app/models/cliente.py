from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.core.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    nome_fantasia = Column(String(100), nullable=True)
    cpf_ou_cnpj = Column(String(18), nullable=False, unique=True, index=True)
    endereco = Column(String(255), nullable=False)
    ponto_referencia = Column(String(255), nullable=True)
    email = Column(String(100), nullable=True)
    telefone1 = Column(String(20), nullable=False)
    telefone2 = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
