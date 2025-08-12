from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import enum

from app.schemas.produto import Produto
from app.core.enums import TipoMedida

class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"

# Schemas para EntradaEstoque
class EntradaEstoqueBase(BaseModel):
    produto_id: int
    tipo_medida: TipoMedida
    preco_custo: Decimal = Field(..., gt=0)
    quantidade: Decimal = Field(..., gt=0)
    fornecedor: Optional[str] = None
    observacoes: Optional[str] = None

class EntradaEstoqueCreate(EntradaEstoqueBase):
    pass

class EntradaEstoque(EntradaEstoqueBase):
    id: int
    valor_total: Decimal
    data_entrada: datetime
    produto: Produto
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schemas para Inventario
class InventarioBase(BaseModel):
    produto_id: int
    tipo_medida: TipoMedida
    quantidade_atual: Decimal = Field(..., ge=0)
    valor_unitario: Decimal = Field(..., gt=0)
    observacoes: Optional[str] = None

class InventarioCreate(InventarioBase):
    pass

class Inventario(InventarioBase):
    id: int
    valor_total: Decimal
    data_ultima_atualizacao: datetime
    produto: Produto
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema para resumo de estoque
class ResumoEstoque(BaseModel):
    produto: Produto
    quantidade_total: Decimal
    valor_total: Decimal
    ultima_entrada: Optional[datetime] = None
    ultimo_inventario: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema para atualização de inventário
class InventarioUpdate(BaseModel):
    quantidade_atual: Decimal = Field(..., ge=0)
    observacoes: Optional[str] = None

# Schema para consulta de estoque
class EstoqueConsulta(BaseModel):
    produto: Produto
    quantidade_atual: Decimal
    estoque_minimo: Decimal
    estoque_baixo: bool
    entradas_recentes: List[EntradaEstoque]
    total_entradas_mes: Decimal
    ultima_atualizacao: Optional[datetime] = None

# Schemas para EstoqueFifo
class EstoqueFifoBase(BaseModel):
    produto_id: int
    entrada_estoque_id: int
    quantidade_restante: Decimal = Field(..., ge=0)
    preco_custo_unitario: Decimal = Field(..., gt=0)
    data_entrada: datetime

class EstoqueFifo(EstoqueFifoBase):
    id: int
    finalizado: bool
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schemas para MovimentacaoCaixa
class MovimentacaoCaixaBase(BaseModel):
    produto_id: int
    tipo_movimentacao: TipoMovimentacao
    quantidade: Decimal = Field(..., gt=0)
    preco_unitario: Decimal = Field(..., gt=0)
    observacoes: Optional[str] = None

class MovimentacaoCaixaCreate(MovimentacaoCaixaBase):
    venda_id: Optional[int] = None
    entrada_estoque_id: Optional[int] = None

class MovimentacaoCaixa(MovimentacaoCaixaBase):
    id: int
    venda_id: Optional[int] = None
    entrada_estoque_id: Optional[int] = None
    valor_total: Decimal
    data_movimentacao: datetime
    criado_em: datetime

    class Config:
        from_attributes = True

# Schemas para LucroBruto
class LucroBrutoBase(BaseModel):
    venda_id: int
    produto_id: int
    quantidade_vendida: Decimal = Field(..., gt=0)
    custo_total: Decimal = Field(..., ge=0)
    receita_total: Decimal = Field(..., gt=0)

class LucroBruto(LucroBrutoBase):
    id: int
    lucro_bruto: Decimal
    margem_percentual: Decimal
    data_calculo: datetime
    criado_em: datetime

    class Config:
        from_attributes = True

# Schema para relatório de fluxo de caixa
class FluxoCaixa(BaseModel):
    produto: Produto
    entradas: List[MovimentacaoCaixa]
    saidas: List[MovimentacaoCaixa]
    total_entradas: Decimal
    total_saidas: Decimal
    saldo: Decimal
    lucro_bruto_total: Decimal
    margem_media: Decimal

# Schema para relatório de rentabilidade
class RelatorioRentabilidade(BaseModel):
    periodo_inicio: datetime
    periodo_fim: datetime
    produtos: List[dict]  # Detalhes por produto
    total_vendas: Decimal
    total_custos: Decimal
    lucro_bruto_total: Decimal
    margem_bruta_media: Decimal
