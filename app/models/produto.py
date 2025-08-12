from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Enum
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.enums import TipoMedida

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(String(255), nullable=True)
    preco_venda = Column(Numeric(10, 2), nullable=False)
    tipo_medida = Column(Enum(TipoMedida), nullable=False, default=TipoMedida.UNIDADE)
    estoque_minimo = Column(Numeric(10, 2), nullable=False, default=0)
    imagem = Column(String(255), nullable=True)  # URL da imagem no Google Drive
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
