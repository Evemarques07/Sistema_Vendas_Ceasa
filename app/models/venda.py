from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.enums import TipoMedida, SituacaoPedido, SituacaoPagamento

class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    funcionario_separacao_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    total_venda = Column(DECIMAL(10, 2), nullable=False)
    situacao_pedido = Column(SQLEnum(SituacaoPedido), default=SituacaoPedido.A_SEPARAR)
    situacao_pagamento = Column(SQLEnum(SituacaoPagamento), default=SituacaoPagamento.PENDENTE)
    observacoes = Column(Text, nullable=True)
    data_venda = Column(DateTime(timezone=True), server_default=func.now())
    data_separacao = Column(DateTime(timezone=True), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cliente = relationship("Cliente")
    funcionario_separacao = relationship("Usuario", foreign_keys=[funcionario_separacao_id])
    itens = relationship("ItemVenda", back_populates="venda")

class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(DECIMAL(10, 3), nullable=False)
    quantidade_real = Column(DECIMAL(10, 3), nullable=True)  # Após separação
    tipo_medida = Column(SQLEnum(TipoMedida), nullable=False)
    valor_unitario = Column(DECIMAL(10, 2), nullable=False)
    valor_total_produto = Column(DECIMAL(10, 2), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")
