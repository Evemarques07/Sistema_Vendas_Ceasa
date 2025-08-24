from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.schemas.cliente import Cliente
from app.schemas.produto import Produto
from app.core.enums import TipoMedida, SituacaoPedido, SituacaoPagamento

# Schemas para ItemVenda
class ItemVendaBase(BaseModel):
    produto_id: int
    quantidade: Decimal = Field(..., gt=0)
    tipo_medida: TipoMedida
    valor_unitario: Decimal = Field(..., gt=0)
    custo: Decimal = Field(..., gt=0)
    lucro_bruto: Decimal = Field(...)

class ItemVendaCreate(ItemVendaBase):
    pass

class ItemVendaUpdate(BaseModel):
    valor_unitario: Optional[Decimal] = None
    custo: Optional[Decimal] = None
    lucro_bruto: Optional[Decimal] = None

class ItemVenda(ItemVendaBase):
    id: int
    venda_id: int
    valor_total_produto: Decimal
    produto: Produto
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schemas para Venda
class VendaBase(BaseModel):
    cliente_id: int
    observacoes: Optional[str] = None

class VendaCreate(VendaBase):
    itens: List[ItemVendaCreate]


class Venda(VendaBase):
    id: int
    total_venda: Decimal
    lucro_bruto_total: Optional[Decimal] = None
    situacao_pagamento: SituacaoPagamento
    data_venda: datetime
    cliente_id: Optional[int] = None
    cliente: Optional[Cliente] = None
    itens: List[ItemVenda]
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


