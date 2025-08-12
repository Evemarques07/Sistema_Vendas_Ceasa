from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, case, text
from decimal import Decimal
from datetime import datetime, date

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.venda import Venda, ItemVenda
from app.core.enums import SituacaoPedido, SituacaoPagamento
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.usuario import Usuario

router = APIRouter()

@router.get("/pagamentos-pendentes", response_model=dict)
async def pagamentos_pendentes_por_cliente(
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente específico"),
    ordenar_por: str = Query("valor_desc", description="Ordenar por: valor_desc, valor_asc, data_desc, data_asc"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 Relatório de Pagamentos Pendentes por Cliente
    
    Mostra todas as vendas que ainda não foram pagas, agrupadas por cliente
    com totais e detalhes de cada venda pendente.
    """
    
    # Query base para vendas pendentes
    query = db.query(Venda).filter(
        Venda.situacao_pagamento == SituacaoPagamento.PENDENTE
    )
    
    # Filtrar por cliente se especificado
    if cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        query = query.filter(Venda.cliente_id == cliente_id)
    
    # Aplicar ordenação
    if ordenar_por == "valor_desc":
        query = query.order_by(desc(Venda.total_venda))
    elif ordenar_por == "valor_asc":
        query = query.order_by(Venda.total_venda)
    elif ordenar_por == "data_desc":
        query = query.order_by(desc(Venda.data_venda))
    elif ordenar_por == "data_asc":
        query = query.order_by(Venda.data_venda)
    
    vendas_pendentes = query.all()
    
    # Agrupar por cliente
    clientes_pendentes = {}
    total_geral_pendente = Decimal('0.00')
    
    for venda in vendas_pendentes:
        cliente_id = venda.cliente_id
        
        if cliente_id not in clientes_pendentes:
            clientes_pendentes[cliente_id] = {
                "cliente": {
                    "id": venda.cliente.id,
                    "nome": venda.cliente.nome,
                    "nome_fantasia": venda.cliente.nome_fantasia,
                    "email": venda.cliente.email,
                    "telefone1": venda.cliente.telefone1
                },
                "vendas_pendentes": [],
                "total_pendente": Decimal('0.00'),
                "quantidade_vendas": 0
            }
        
        clientes_pendentes[cliente_id]["vendas_pendentes"].append({
            "id": venda.id,
            "data_venda": venda.data_venda,
            "total_venda": float(venda.total_venda),
            "situacao_pedido": venda.situacao_pedido.value,
            "observacoes": venda.observacoes,
            "dias_pendente": (datetime.now() - venda.data_venda).days
        })
        
        clientes_pendentes[cliente_id]["total_pendente"] += venda.total_venda
        clientes_pendentes[cliente_id]["quantidade_vendas"] += 1
        total_geral_pendente += venda.total_venda
    
    # Converter para lista e ordenar por total pendente
    resultado = list(clientes_pendentes.values())
    resultado.sort(key=lambda x: x["total_pendente"], reverse=True)
    
    # Converter Decimal para float para serialização
    for cliente in resultado:
        cliente["total_pendente"] = float(cliente["total_pendente"])
    
    return {
        "data": {
            "clientes": resultado,
            "resumo": {
                "total_geral_pendente": float(total_geral_pendente),
                "quantidade_clientes": len(resultado),
                "quantidade_vendas_pendentes": len(vendas_pendentes)
            }
        },
        "message": "Relatório de pagamentos pendentes gerado com sucesso",
        "success": True
    }

@router.get("/historico-vendas/{cliente_id}", response_model=dict)
async def historico_vendas_cliente(
    cliente_id: int,
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    situacao_pagamento: Optional[SituacaoPagamento] = Query(None, description="Filtrar por situação do pagamento"),
    skip: int = Query(0, ge=0, description="Registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Registros por página"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📈 Histórico Completo de Vendas por Cliente
    
    Mostra todas as vendas de um cliente específico com filtros por período
    e situação de pagamento, incluindo estatísticas detalhadas.
    """
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Query base
    query = db.query(Venda).filter(Venda.cliente_id == cliente_id)
    
    # Aplicar filtros de data
    if data_inicio:
        query = query.filter(Venda.data_venda >= data_inicio)
    if data_fim:
        query = query.filter(Venda.data_venda <= data_fim)
    
    # Filtrar por situação de pagamento
    if situacao_pagamento:
        query = query.filter(Venda.situacao_pagamento == situacao_pagamento)
    
    # Contar total antes da paginação
    total_vendas = query.count()
    
    # Aplicar paginação e ordenação
    vendas = query.order_by(desc(Venda.data_venda)).offset(skip).limit(limit).all()
    
    # Calcular estatísticas
    query_stats = db.query(Venda).filter(Venda.cliente_id == cliente_id)
    if data_inicio:
        query_stats = query_stats.filter(Venda.data_venda >= data_inicio)
    if data_fim:
        query_stats = query_stats.filter(Venda.data_venda <= data_fim)
    if situacao_pagamento:
        query_stats = query_stats.filter(Venda.situacao_pagamento == situacao_pagamento)
    
    estatisticas = query_stats.with_entities(
        func.sum(Venda.total_venda).label('total_vendido'),
        func.avg(Venda.total_venda).label('ticket_medio'),
        func.count(Venda.id).label('quantidade_vendas'),
        func.sum(case((Venda.situacao_pagamento == SituacaoPagamento.PENDENTE, Venda.total_venda), else_=0)).label('total_pendente'),
        func.sum(case((Venda.situacao_pagamento == SituacaoPagamento.PAGO, Venda.total_venda), else_=0)).label('total_pago')
    ).first()
    
    # Formatar vendas para resposta
    vendas_formatadas = []
    for venda in vendas:
        funcionario_separacao = None
        if venda.funcionario_separacao:
            funcionario_separacao = {
                "id": venda.funcionario_separacao.id,
                "nome": venda.funcionario_separacao.nome,
                "email": venda.funcionario_separacao.email
            }
        
        vendas_formatadas.append({
            "id": venda.id,
            "data_venda": venda.data_venda,
            "data_separacao": venda.data_separacao,
            "total_venda": float(venda.total_venda),
            "situacao_pedido": venda.situacao_pedido.value,
            "situacao_pagamento": venda.situacao_pagamento.value,
            "observacoes": venda.observacoes,
            "funcionario_separacao": funcionario_separacao,
            "quantidade_itens": len(venda.itens)
        })
    
    return {
        "data": {
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "nome_fantasia": cliente.nome_fantasia,
                "email": cliente.email,
                "telefone1": cliente.telefone1
            },
            "vendas": vendas_formatadas,
            "estatisticas": {
                "total_vendido": float(estatisticas.total_vendido or 0),
                "ticket_medio": float(estatisticas.ticket_medio or 0),
                "quantidade_vendas": estatisticas.quantidade_vendas or 0,
                "total_pendente": float(estatisticas.total_pendente or 0),
                "total_pago": float(estatisticas.total_pago or 0)
            },
            "paginacao": {
                "pagina": (skip // limit) + 1,
                "itens_por_pagina": limit,
                "total_itens": total_vendas,
                "total_paginas": (total_vendas + limit - 1) // limit
            }
        },
        "message": f"Histórico de vendas do cliente {cliente.nome} obtido com sucesso",
        "success": True
    }

@router.get("/resumo-financeiro/{cliente_id}", response_model=dict)
async def resumo_financeiro_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    💰 Resumo Financeiro Completo por Cliente
    
    Dashboard com todas as informações financeiras importantes de um cliente:
    - Total de vendas (histórico completo)
    - Valores pendentes e pagos
    - Produtos mais comprados
    - Evolução mensal
    """
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Estatísticas gerais
    stats_gerais = db.query(
        func.sum(Venda.total_venda).label('total_historico'),
        func.avg(Venda.total_venda).label('ticket_medio'),
        func.count(Venda.id).label('total_vendas'),
        func.sum(case((Venda.situacao_pagamento == SituacaoPagamento.PENDENTE, Venda.total_venda), else_=0)).label('total_pendente'),
        func.sum(case((Venda.situacao_pagamento == SituacaoPagamento.PAGO, Venda.total_venda), else_=0)).label('total_pago'),
        func.min(Venda.data_venda).label('primeira_compra'),
        func.max(Venda.data_venda).label('ultima_compra')
    ).filter(Venda.cliente_id == cliente_id).first()
    
    # Produtos mais comprados
    produtos_mais_comprados = db.query(
        Produto.nome,
        func.sum(ItemVenda.quantidade).label('quantidade_total'),
        func.sum(ItemVenda.valor_total_produto).label('valor_total'),
        func.count(ItemVenda.id).label('vezes_comprado')
    ).join(ItemVenda, Produto.id == ItemVenda.produto_id)\
     .join(Venda, ItemVenda.venda_id == Venda.id)\
     .filter(Venda.cliente_id == cliente_id)\
     .group_by(Produto.id, Produto.nome)\
     .order_by(desc(func.sum(ItemVenda.valor_total_produto)))\
     .limit(10).all()
    
    # Evolução mensal (últimos 12 meses)
    evolucao_mensal = db.query(
        func.date_format(Venda.data_venda, '%Y-%m').label('mes'),
        func.sum(Venda.total_venda).label('total_mes'),
        func.count(Venda.id).label('vendas_mes')
    ).filter(Venda.cliente_id == cliente_id)\
     .filter(Venda.data_venda >= func.date_sub(func.now(), text('INTERVAL 12 MONTH')))\
     .group_by(func.date_format(Venda.data_venda, '%Y-%m'))\
     .order_by(func.date_format(Venda.data_venda, '%Y-%m')).all()
    
    # Últimas vendas não pagas
    vendas_pendentes = db.query(Venda).filter(
        and_(
            Venda.cliente_id == cliente_id,
            Venda.situacao_pagamento == SituacaoPagamento.PENDENTE
        )
    ).order_by(desc(Venda.data_venda)).limit(5).all()
    
    return {
        "data": {
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "nome_fantasia": cliente.nome_fantasia,
                "email": cliente.email,
                "telefone1": cliente.telefone1,
                "ativo": cliente.ativo
            },
            "estatisticas_gerais": {
                "total_historico": float(stats_gerais.total_historico or 0),
                "ticket_medio": float(stats_gerais.ticket_medio or 0),
                "total_vendas": stats_gerais.total_vendas or 0,
                "total_pendente": float(stats_gerais.total_pendente or 0),
                "total_pago": float(stats_gerais.total_pago or 0),
                "primeira_compra": stats_gerais.primeira_compra,
                "ultima_compra": stats_gerais.ultima_compra,
                "percentual_inadimplencia": float((stats_gerais.total_pendente or 0) / (stats_gerais.total_historico or 1) * 100)
            },
            "produtos_favoritos": [
                {
                    "nome": produto.nome,
                    "quantidade_total": float(produto.quantidade_total),
                    "valor_total": float(produto.valor_total),
                    "vezes_comprado": produto.vezes_comprado
                }
                for produto in produtos_mais_comprados
            ],
            "evolucao_mensal": [
                {
                    "mes": evolucao.mes,
                    "total_vendido": float(evolucao.total_mes),
                    "quantidade_vendas": evolucao.vendas_mes
                }
                for evolucao in evolucao_mensal
            ],
            "vendas_pendentes_recentes": [
                {
                    "id": venda.id,
                    "data_venda": venda.data_venda,
                    "total_venda": float(venda.total_venda),
                    "dias_pendente": (datetime.now() - venda.data_venda).days,
                    "observacoes": venda.observacoes
                }
                for venda in vendas_pendentes
            ]
        },
        "message": f"Resumo financeiro do cliente {cliente.nome} gerado com sucesso",
        "success": True
    }

@router.get("/dashboard-vendas", response_model=dict)
async def dashboard_vendas_periodo(
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    current_user: Usuario = Depends(get_current_admin_user),  # Só admin pode ver dashboard geral
    db: Session = Depends(get_db)
):
    """
    📊 Dashboard Geral de Vendas por Período
    
    Visão executiva com KPIs principais:
    - Faturamento total e por situação
    - Top clientes
    - Top produtos
    - Performance de funcionários
    - Indicadores de inadimplência
    """
    
    # Query base com filtros de data
    query_base = db.query(Venda)
    if data_inicio:
        query_base = query_base.filter(Venda.data_venda >= data_inicio)
    if data_fim:
        query_base = query_base.filter(Venda.data_venda <= data_fim)
    
    # KPIs principais
    kpis = query_base.with_entities(
        func.sum(Venda.total_venda).label('faturamento_total'),
        func.avg(Venda.total_venda).label('ticket_medio'),
        func.count(Venda.id).label('total_vendas'),
        func.sum(case((Venda.situacao_pagamento == SituacaoPagamento.PAGO, Venda.total_venda), else_=0)).label('total_pago'),
        func.sum(case((Venda.situacao_pagamento == SituacaoPagamento.PENDENTE, Venda.total_venda), else_=0)).label('total_pendente'),
        func.sum(case((Venda.situacao_pedido == SituacaoPedido.SEPARADO, 1), else_=0)).label('vendas_separadas'),
        func.sum(case((Venda.situacao_pedido == SituacaoPedido.A_SEPARAR, 1), else_=0)).label('vendas_a_separar')
    ).first()
    
    # Top 10 clientes por faturamento
    top_clientes = db.query(
        Cliente.nome,
        Cliente.nome_fantasia,
        func.sum(Venda.total_venda).label('total_comprado'),
        func.count(Venda.id).label('quantidade_compras'),
        func.sum(case((Venda.situacao_pagamento == SituacaoPagamento.PENDENTE, Venda.total_venda), else_=0)).label('pendente')
    ).join(Venda, Cliente.id == Venda.cliente_id)
    
    if data_inicio:
        top_clientes = top_clientes.filter(Venda.data_venda >= data_inicio)
    if data_fim:
        top_clientes = top_clientes.filter(Venda.data_venda <= data_fim)
        
    top_clientes = top_clientes.group_by(Cliente.id, Cliente.nome, Cliente.nome_fantasia)\
                              .order_by(desc(func.sum(Venda.total_venda)))\
                              .limit(10).all()
    
    # Top 10 produtos mais vendidos
    top_produtos = db.query(
        Produto.nome,
        func.sum(ItemVenda.quantidade).label('quantidade_vendida'),
        func.sum(ItemVenda.valor_total_produto).label('faturamento_produto')
    ).join(ItemVenda, Produto.id == ItemVenda.produto_id)\
     .join(Venda, ItemVenda.venda_id == Venda.id)
    
    if data_inicio:
        top_produtos = top_produtos.filter(Venda.data_venda >= data_inicio)
    if data_fim:
        top_produtos = top_produtos.filter(Venda.data_venda <= data_fim)
        
    top_produtos = top_produtos.group_by(Produto.id, Produto.nome)\
                              .order_by(desc(func.sum(ItemVenda.valor_total_produto)))\
                              .limit(10).all()
    
    # Performance de funcionários (separações)
    performance_funcionarios = db.query(
        Usuario.nome,
        Usuario.email,
        func.count(Venda.id).label('vendas_separadas'),
        func.sum(Venda.total_venda).label('valor_separado')
    ).join(Venda, Usuario.id == Venda.funcionario_separacao_id)\
     .filter(Venda.funcionario_separacao_id.isnot(None))
    
    if data_inicio:
        performance_funcionarios = performance_funcionarios.filter(Venda.data_separacao >= data_inicio)
    if data_fim:
        performance_funcionarios = performance_funcionarios.filter(Venda.data_separacao <= data_fim)
        
    performance_funcionarios = performance_funcionarios.group_by(Usuario.id, Usuario.nome, Usuario.email)\
                                                      .order_by(desc(func.count(Venda.id))).all()
    
    return {
        "data": {
            "periodo": {
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "gerado_em": datetime.now()
            },
            "kpis": {
                "faturamento_total": float(kpis.faturamento_total or 0),
                "ticket_medio": float(kpis.ticket_medio or 0),
                "total_vendas": kpis.total_vendas or 0,
                "total_pago": float(kpis.total_pago or 0),
                "total_pendente": float(kpis.total_pendente or 0),
                "taxa_inadimplencia": float((kpis.total_pendente or 0) / (kpis.faturamento_total or 1) * 100),
                "vendas_separadas": kpis.vendas_separadas or 0,
                "vendas_a_separar": kpis.vendas_a_separar or 0,
                "taxa_separacao": float((kpis.vendas_separadas or 0) / (kpis.total_vendas or 1) * 100)
            },
            "top_clientes": [
                {
                    "nome": cliente.nome,
                    "nome_fantasia": cliente.nome_fantasia,
                    "total_comprado": float(cliente.total_comprado),
                    "quantidade_compras": cliente.quantidade_compras,
                    "valor_pendente": float(cliente.pendente)
                }
                for cliente in top_clientes
            ],
            "top_produtos": [
                {
                    "nome": produto.nome,
                    "quantidade_vendida": float(produto.quantidade_vendida),
                    "faturamento": float(produto.faturamento_produto)
                }
                for produto in top_produtos
            ],
            "performance_funcionarios": [
                {
                    "nome": func.nome,
                    "email": func.email,
                    "vendas_separadas": func.vendas_separadas,
                    "valor_separado": float(func.valor_separado)
                }
                for func in performance_funcionarios
            ]
        },
        "message": "Dashboard de vendas gerado com sucesso",
        "success": True
    }

@router.get("/clientes-inadimplentes", response_model=dict)
async def clientes_inadimplentes(
    dias_minimo: int = Query(30, description="Mínimo de dias em atraso"),
    valor_minimo: Optional[float] = Query(None, description="Valor mínimo em débito"),
    ordenar_por: str = Query("valor_desc", description="Ordenar por: valor_desc, valor_asc, dias_desc, dias_asc"),
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    🚨 Relatório de Clientes Inadimplentes
    
    Lista clientes com pagamentos em atraso, ordenados por critérios específicos.
    Útil para ações de cobrança e controle de crédito.
    """
    
    # Buscar vendas pendentes há mais de X dias - usar text() para MySQL
    data_limite = func.date_sub(func.now(), text(f'INTERVAL {dias_minimo} DAY'))
    
    query = db.query(
        Cliente.id,
        Cliente.nome,
        Cliente.nome_fantasia,
        Cliente.email,
        Cliente.telefone1,
        func.sum(Venda.total_venda).label('total_devido'),
        func.count(Venda.id).label('vendas_pendentes'),
        func.min(Venda.data_venda).label('venda_mais_antiga'),
        func.max(Venda.data_venda).label('venda_mais_recente')
    ).join(Venda, Cliente.id == Venda.cliente_id)\
     .filter(
        and_(
            Venda.situacao_pagamento == SituacaoPagamento.PENDENTE,
            Venda.data_venda <= data_limite
        )
    ).group_by(Cliente.id, Cliente.nome, Cliente.nome_fantasia, Cliente.email, Cliente.telefone1)
    
    # Filtrar por valor mínimo se especificado
    if valor_minimo:
        query = query.having(func.sum(Venda.total_venda) >= valor_minimo)
    
    # Aplicar ordenação
    if ordenar_por == "valor_desc":
        query = query.order_by(desc(func.sum(Venda.total_venda)))
    elif ordenar_por == "valor_asc":
        query = query.order_by(func.sum(Venda.total_venda))
    elif ordenar_por == "dias_desc":
        query = query.order_by(func.min(Venda.data_venda))
    elif ordenar_por == "dias_asc":
        query = query.order_by(desc(func.min(Venda.data_venda)))
    
    inadimplentes = query.all()
    
    # Formatar resultado
    resultado = []
    total_devido_geral = Decimal('0.00')
    
    for cliente in inadimplentes:
        dias_atraso = (datetime.now().date() - cliente.venda_mais_antiga.date()).days
        
        resultado.append({
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "nome_fantasia": cliente.nome_fantasia,
                "email": cliente.email,
                "telefone1": cliente.telefone1
            },
            "divida": {
                "total_devido": float(cliente.total_devido),
                "vendas_pendentes": cliente.vendas_pendentes,
                "venda_mais_antiga": cliente.venda_mais_antiga,
                "venda_mais_recente": cliente.venda_mais_recente,
                "dias_atraso_maximo": dias_atraso
            }
        })
        
        total_devido_geral += cliente.total_devido
    
    return {
        "data": {
            "clientes_inadimplentes": resultado,
            "resumo": {
                "total_devido_geral": float(total_devido_geral),
                "quantidade_clientes": len(resultado),
                "criterios": {
                    "dias_minimo_atraso": dias_minimo,
                    "valor_minimo": valor_minimo,
                    "ordenacao": ordenar_por
                }
            }
        },
        "message": f"Encontrados {len(resultado)} clientes inadimplentes",
        "success": True
    }
