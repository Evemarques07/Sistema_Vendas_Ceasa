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

class ItemVendaCreate(ItemVendaBase):
    pass

class ItemVendaUpdate(BaseModel):
    quantidade_real: Optional[Decimal] = Field(None, gt=0)

class ItemVenda(ItemVendaBase):
    id: int
    venda_id: int
    quantidade_real: Optional[Decimal] = None
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

class VendaUpdate(BaseModel):
    situacao_pedido: Optional[SituacaoPedido] = None
    situacao_pagamento: Optional[SituacaoPagamento] = None
    observacoes: Optional[str] = None

class Venda(VendaBase):
    id: int
    funcionario_separacao_id: Optional[int] = None
    total_venda: Decimal
    situacao_pedido: SituacaoPedido
    situacao_pagamento: SituacaoPagamento
    data_venda: datetime
    data_separacao: Optional[datetime] = None
    funcionario_separacao: Optional[dict] = None  # {"id": int, "nome": str, "email": str}
    cliente_id: Optional[int] = None
    cliente: Optional[Cliente] = None
    itens: List[ItemVenda]
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm para incluir dados do funcionário de separação"""
        data = {
            "id": obj.id,
            "cliente_id": obj.cliente_id,
            "funcionario_separacao_id": obj.funcionario_separacao_id,
            "total_venda": obj.total_venda,
            "situacao_pedido": obj.situacao_pedido,
            "situacao_pagamento": obj.situacao_pagamento,
            "observacoes": obj.observacoes,
            "data_venda": obj.data_venda,
            "data_separacao": obj.data_separacao,
            "criado_em": obj.criado_em,
            "atualizado_em": obj.atualizado_em,
            "cliente": obj.cliente,
            "itens": obj.itens,
        }
        
        # Incluir dados do funcionário de separação se existir
        if obj.funcionario_separacao:
            data["funcionario_separacao"] = {
                "id": obj.funcionario_separacao.id,
                "nome": obj.funcionario_separacao.nome,
                "email": obj.funcionario_separacao.email
            }
        
        return cls(**data)

    class Config:
        from_attributes = True

# Schema para atualizar separação
class SeparacaoUpdate(BaseModel):
    produtos_separados: List[dict]  # [{"produto_id": int, "quantidade_real": Decimal}]
