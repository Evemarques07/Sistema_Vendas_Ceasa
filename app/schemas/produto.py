from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.core.enums import TipoMedida

# Schemas base para Produto
class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)
    preco_venda: Decimal = Field(..., gt=0)
    tipo_medida: TipoMedida = TipoMedida.UNIDADE
    estoque_minimo: Decimal = Field(default=0, ge=0)
    ativo: bool = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)
    preco_venda: Optional[Decimal] = Field(None, gt=0)
    tipo_medida: Optional[TipoMedida] = None
    estoque_minimo: Optional[Decimal] = Field(None, ge=0)
    ativo: Optional[bool] = None

class Produto(ProdutoBase):
    id: int
    imagem: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True
