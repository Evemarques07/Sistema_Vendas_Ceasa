from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from decimal import Decimal

from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.venda import Venda, ItemVenda
from app.core.enums import SituacaoPedido, SituacaoPagamento
 
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.utils.timezone import now_brazil
from app.schemas.venda import (
    Venda as VendaSchema,
    VendaCreate
)
# Removido fluxo de caixa e estoque
#utcnow
router = APIRouter()

@router.get("/", response_model=dict)
async def listar_vendas(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    situacao_pedido: Optional[SituacaoPedido] = Query(None, description="Filtrar por situação do pedido"),
    situacao_pagamento: Optional[SituacaoPagamento] = Query(None, description="Filtrar por situação do pagamento"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar vendas com filtros e paginação"""
    query = db.query(Venda)
    
    # Apply filters
    if cliente_id:
        query = query.filter(Venda.cliente_id == cliente_id)
    
    if situacao_pedido:
        query = query.filter(Venda.situacao_pedido == situacao_pedido)
    
    if situacao_pagamento:
        query = query.filter(Venda.situacao_pagamento == situacao_pagamento)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by date
    vendas = query.order_by(Venda.data_venda.desc()).offset(skip).limit(limit).all()
    
    return {
        "data": {
            "items": [VendaSchema.from_orm(venda) for venda in vendas],
            "paginacao": {
                "pagina": (skip // limit) + 1,
                "itensPorPagina": limit,
                "totalItens": total,
                "totalPaginas": (total + limit - 1) // limit
            }
        },
        "message": "Vendas listadas com sucesso",
        "success": True
    }

@router.get("/dashboard", response_model=dict)
async def obter_dashboard_vendas(
    data_inicio: Optional[str] = Query(None, description="Data de início (YYYY-MM-DD). Se não informada, usa hoje"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dashboard com estatísticas de vendas e clientes"""
    from datetime import datetime, date, timedelta, time
    from sqlalchemy import func, and_, extract
    from app.models.cliente import Cliente
    
    # Definir datas
    hoje = date.today()
    
    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD"
            )
    else:
        data_inicio_dt = hoje
    
    data_fim_dt = hoje
    
    # Se a data de início for diferente de hoje, criar período
    if data_inicio_dt != hoje:
        # Período: da data informada até hoje (incluindo todo o dia de hoje)
        data_inicio_completa = datetime.combine(data_inicio_dt, time.min)  # 00:00:00
        data_fim_completa = datetime.combine(data_fim_dt, time.max)        # 23:59:59
        
        vendas_periodo_query = db.query(Venda).filter(
            and_(
                Venda.data_venda >= data_inicio_completa,
                Venda.data_venda <= data_fim_completa
            )
        )
        periodo_texto = f"de {data_inicio_dt.strftime('%d/%m/%Y')} até {data_fim_dt.strftime('%d/%m/%Y')}"
    else:
        # Apenas hoje (todo o dia)
        inicio_hoje = datetime.combine(hoje, time.min)  # 00:00:00
        fim_hoje = datetime.combine(hoje, time.max)     # 23:59:59
        
        vendas_periodo_query = db.query(Venda).filter(
            and_(
                Venda.data_venda >= inicio_hoje,
                Venda.data_venda <= fim_hoje
            )
        )
        periodo_texto = f"de hoje ({hoje.strftime('%d/%m/%Y')})"
    
    # Vendas do período
    vendas_periodo = vendas_periodo_query.all()
    total_vendas_periodo = len(vendas_periodo)
    valor_total_vendas = sum(float(v.total_venda) for v in vendas_periodo)
    lucro_bruto_total = sum(float(v.lucro_bruto_total or 0) for v in vendas_periodo)
    ticket_medio = (valor_total_vendas / total_vendas_periodo) if total_vendas_periodo > 0 else 0

    # Estatísticas de clientes
    total_clientes = db.query(Cliente).count()
    total_clientes_ativos = db.query(Cliente).filter(Cliente.ativo == True).count()

    # Vendas mensais (últimos 12 meses)
    from collections import OrderedDict
    vendas_mensais = OrderedDict()
    for i in range(11, -1, -1):
        mes_ref = (hoje.month - i - 1) % 12 + 1
        ano_ref = hoje.year if hoje.month - i > 0 else hoje.year - 1
        vendas_mes = db.query(
            func.count(Venda.id),
            func.sum(Venda.total_venda),
            func.sum(Venda.lucro_bruto_total)
        ).filter(
            extract('month', Venda.data_venda) == mes_ref,
            extract('year', Venda.data_venda) == ano_ref
        ).first()
        vendas_mensais[f"{mes_ref:02d}/{ano_ref}"] = {
            "quantidade": vendas_mes[0] or 0,
            "valor_total": float(vendas_mes[1] or 0),
            "lucro_bruto_total": float(vendas_mes[2] or 0)
        }

    # Pagamentos pendentes
    vendas_pendentes = db.query(Venda).filter(
        Venda.situacao_pagamento == SituacaoPagamento.PENDENTE
    ).all()
    total_pagamentos_pendentes = sum(float(v.total_venda) for v in vendas_pendentes)

    # Ranking de clientes (top 5)
    ranking_clientes = (
        db.query(
            Cliente.nome,
            func.count(Venda.id).label('qtd_vendas'),
            func.sum(Venda.total_venda).label('valor_total'),
            func.sum(Venda.lucro_bruto_total).label('lucro_total')
        )
        .join(Venda, Venda.cliente_id == Cliente.id)
        .group_by(Cliente.id)
        .order_by(func.sum(Venda.total_venda).desc())
        .limit(5)
        .all()
    )
    ranking_clientes_list = [
        {
            "cliente": r.nome,
            "qtd_vendas": r.qtd_vendas,
            "valor_total": float(r.valor_total or 0),
            "lucro_total": float(r.lucro_total or 0)
        } for r in ranking_clientes
    ]

    dashboard = {
        "periodo": {
            "data_inicio": data_inicio_dt.strftime("%Y-%m-%d"),
            "data_fim": data_fim_dt.strftime("%Y-%m-%d"),
            "descricao": periodo_texto
        },
        "vendas_periodo": {
            "total_vendas": total_vendas_periodo,
            "valor_total": valor_total_vendas,
            "lucro_bruto_total": lucro_bruto_total,
            "ticket_medio": round(ticket_medio, 2)
        },
        "estatisticas_clientes": {
            "total_clientes": total_clientes,
            "clientes_ativos": total_clientes_ativos,
            "clientes_inativos": total_clientes - total_clientes_ativos
        },
        "vendas_mensais": vendas_mensais,
        "pagamentos_pendentes": {
            "quantidade_vendas": len(vendas_pendentes),
            "valor_total": total_pagamentos_pendentes,
            "vendas": [
                {
                    "id": v.id,
                    "cliente": v.cliente.nome if v.cliente else "Cliente não encontrado",
                    "valor": float(v.total_venda),
                    "data_venda": v.data_venda.strftime("%Y-%m-%d %H:%M:%S"),
                    "dias_pendente": (hoje - v.data_venda.date()).days
                } for v in vendas_pendentes
            ]
        },
        "ranking_clientes": ranking_clientes_list
    }

    return {
        "data": dashboard,
        "message": f"Dashboard de vendas obtido com sucesso - {periodo_texto}",
        "success": True
    }

@router.get("/{venda_id}", response_model=dict)
async def obter_venda(
    venda_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter venda por ID com cálculo de lucro bruto"""
    from app.models.estoque import LucroBruto
    
    venda = db.query(Venda).filter(Venda.id == venda_id).first()
    if not venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Converter venda para schema
    venda_data = VendaSchema.from_orm(venda)
    
    # Calcular lucro bruto total se a venda foi separada
    lucro_bruto_info = {
        "receita_total": float(venda.total_venda),
        "custo_total": 0.0,
        "lucro_bruto": 0.0,
        "margem_bruta_percentual": 0.0,
        "status_calculo": "não_separado"
    }
    
    if venda.situacao_pedido == SituacaoPedido.SEPARADO:
        # Buscar registros de lucro bruto desta venda (calculados pelo FIFO)
        lucros_produtos = db.query(LucroBruto).filter(
            LucroBruto.venda_id == venda_id
        ).all()
        
        if lucros_produtos:
            # Somar todos os lucros dos produtos desta venda
            custo_total = sum(float(lucro.custo_total) for lucro in lucros_produtos)
            receita_total = sum(float(lucro.receita_total) for lucro in lucros_produtos)
            lucro_bruto_total = sum(float(lucro.lucro_bruto) for lucro in lucros_produtos)
            
            # Calcular margem bruta
            margem_bruta = (lucro_bruto_total / receita_total * 100) if receita_total > 0 else 0
            
            lucro_bruto_info = {
                "receita_total": receita_total,
                "custo_total": custo_total,
                "lucro_bruto": lucro_bruto_total,
                "margem_bruta_percentual": round(margem_bruta, 2),
                "status_calculo": "calculado_fifo",
                "detalhes_produtos": [
                    {
                        "produto_id": lucro.produto_id,
                        "produto_nome": lucro.produto.nome if lucro.produto else "N/A",
                        "quantidade_vendida": float(lucro.quantidade_vendida),
                        "receita_produto": float(lucro.receita_total),
                        "custo_produto": float(lucro.custo_total),
                        "lucro_produto": float(lucro.lucro_bruto),
                        "margem_produto": float(lucro.margem_percentual)
                    }
                    for lucro in lucros_produtos
                ]
            }
        else:
            lucro_bruto_info["status_calculo"] = "separado_sem_calculo"
    
    # Adicionar informações de lucro aos dados da venda
    response_data = venda_data.dict()
    response_data["lucro_bruto"] = lucro_bruto_info
    
    return {
        "data": response_data,
        "message": "Venda obtida com sucesso",
        "success": True
    }

@router.post("/", response_model=dict)
async def criar_venda(
    venda_data: VendaCreate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Criar nova venda (apenas administradores)"""
    # Verify client exists
    cliente = db.query(Cliente).filter(Cliente.id == venda_data.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verify all products exist
    total_venda = Decimal('0.00')
    for item in venda_data.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item.produto_id} não encontrado"
            )
        
        # Calculate item total
        item_total = item.quantidade * item.valor_unitario
        total_venda += item_total
    
    # Calcular lucro_bruto_total
    lucro_bruto_total = sum([item.lucro_bruto for item in venda_data.itens])

    # Create venda
    db_venda = Venda(
        cliente_id=venda_data.cliente_id,
        total_venda=total_venda,
        observacoes=venda_data.observacoes,
        lucro_bruto_total=lucro_bruto_total
    )
    db.add(db_venda)
    db.flush()  # Get the ID

    # Create items
    for item in venda_data.itens:
        item_total = item.quantidade * item.valor_unitario
        db_item = ItemVenda(
            venda_id=db_venda.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            tipo_medida=item.tipo_medida,
            valor_unitario=item.valor_unitario,
            custo=item.custo,
            lucro_bruto=item.lucro_bruto,
            valor_total_produto=item_total
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_venda)

    return {
        "data": VendaSchema.from_orm(db_venda),
        "message": "Venda criada com sucesso",
        "success": True
    }







@router.put("/{venda_id}/pagamento", response_model=dict)
async def marcar_como_pago(
    venda_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Marcar venda como paga"""
    venda = db.query(Venda).filter(Venda.id == venda_id).first()
    if not venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    venda.situacao_pagamento = SituacaoPagamento.PAGO
    db.commit()
    db.refresh(venda)
    
    return {
        "data": VendaSchema.from_orm(venda),
        "message": "Venda marcada como paga",
        "success": True
    }

@router.delete("/{venda_id}", response_model=dict)
async def excluir_venda(
    venda_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Exclui uma venda e retorna os produtos ao estoque.
    Só permite excluir vendas criadas há menos de 24h.
    """
    

    venda = db.query(Venda).filter(Venda.id == venda_id).first()
    if not venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )

    # Verifica se a venda foi criada há menos de 24h
    if (now_brazil() - venda.data_venda).total_seconds() > 86400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível excluir vendas criadas há menos de 24 horas"
        )

    # Retorna os produtos ao estoque
    itens = db.query(ItemVenda).filter(ItemVenda.venda_id == venda_id).all()
    for item in itens:
        inventario = db.query(Inventario).filter(Inventario.produto_id == item.produto_id).first()
        if inventario:
            quantidade = item.quantidade_real if item.quantidade_real is not None else item.quantidade
            inventario.quantidade_atual += quantidade
            inventario.data_ultima_atualizacao = now_brazil()

    # Exclui registros de lucro bruto relacionados à venda
    db.query(LucroBruto).filter(LucroBruto.venda_id == venda_id).delete()

    # Exclui registros de movimentação de caixa relacionados à venda
    db.query(MovimentacaoCaixa).filter(MovimentacaoCaixa.venda_id == venda_id).delete(synchronize_session=False)

    # Exclui os itens e a venda
    for item in itens:
        db.delete(item)
    db.delete(venda)
    db.commit()

    return {
        "message": "Venda excluída e produtos retornados ao estoque com sucesso.",
        "success": True
    }