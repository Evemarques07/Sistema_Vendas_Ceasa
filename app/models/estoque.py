from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, DateTime, Text, Enum as SQLEnum, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base
from app.core.enums import TipoMedida

class TipoMovimentacao(enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"

class EntradaEstoque(Base):
    __tablename__ = "entradas_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    tipo_medida = Column(SQLEnum(TipoMedida), nullable=False)
    preco_custo = Column(DECIMAL(10, 2), nullable=False)
    quantidade = Column(DECIMAL(10, 3), nullable=False)
    valor_total = Column(DECIMAL(10, 2), nullable=False)
    fornecedor = Column(String(200), nullable=True)
    observacoes = Column(Text, nullable=True)
    data_entrada = Column(DateTime(timezone=True), server_default=func.now())
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    produto = relationship("Produto")

class Inventario(Base):
    __tablename__ = "inventarios"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    tipo_medida = Column(SQLEnum(TipoMedida), nullable=False)
    quantidade_atual = Column(DECIMAL(10, 3), nullable=False)
    valor_unitario = Column(DECIMAL(10, 2), nullable=False)
    valor_total = Column(DECIMAL(10, 2), nullable=False)
    observacoes = Column(Text, nullable=True)
    data_ultima_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    produto = relationship("Produto")

class EstoqueFifo(Base):
    """Controle de estoque FIFO (First In, First Out) para cálculo de custos"""
    __tablename__ = "estoque_fifo"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    entrada_estoque_id = Column(Integer, ForeignKey("entradas_estoque.id"), nullable=False)
    quantidade_restante = Column(DECIMAL(10, 3), nullable=False)
    preco_custo_unitario = Column(DECIMAL(10, 2), nullable=False)
    data_entrada = Column(DateTime(timezone=True), nullable=False)
    finalizado = Column(Boolean, default=False, nullable=False)  # True quando quantidade_restante = 0
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    produto = relationship("Produto")
    entrada_estoque = relationship("EntradaEstoque")

class MovimentacaoCaixa(Base):
    """Registro de movimentações financeiras do estoque"""
    __tablename__ = "movimentacoes_caixa"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=True)  # NULL para entradas
    entrada_estoque_id = Column(Integer, ForeignKey("entradas_estoque.id"), nullable=True)  # NULL para saídas
    tipo_movimentacao = Column(SQLEnum(TipoMovimentacao), nullable=False)
    quantidade = Column(DECIMAL(10, 3), nullable=False)
    preco_unitario = Column(DECIMAL(10, 2), nullable=False)
    valor_total = Column(DECIMAL(10, 2), nullable=False)
    data_movimentacao = Column(DateTime(timezone=True), server_default=func.now())
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    produto = relationship("Produto")
    venda = relationship("Venda", foreign_keys=[venda_id])
    entrada_estoque = relationship("EntradaEstoque")

class LucroBruto(Base):
    """Cálculo de lucro bruto por venda"""
    __tablename__ = "lucros_brutos"

    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade_vendida = Column(DECIMAL(10, 3), nullable=False)
    custo_total = Column(DECIMAL(10, 2), nullable=False)  # Soma dos custos FIFO
    receita_total = Column(DECIMAL(10, 2), nullable=False)  # Preço de venda × quantidade
    lucro_bruto = Column(DECIMAL(10, 2), nullable=False)  # receita_total - custo_total
    margem_percentual = Column(DECIMAL(5, 2), nullable=False)  # (lucro_bruto / receita_total) * 100
    data_calculo = Column(DateTime(timezone=True), server_default=func.now())
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    venda = relationship("Venda")
    produto = relationship("Produto")
