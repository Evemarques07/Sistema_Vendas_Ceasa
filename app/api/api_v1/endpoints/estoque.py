from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, func
from decimal import Decimal
from datetime import datetime, date

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.estoque import EntradaEstoque, Inventario
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.estoque import (
    EntradaEstoque as EntradaEstoqueSchema,
    EntradaEstoqueCreate,
    Inventario as InventarioSchema,
    InventarioUpdate,
    EstoqueConsulta,
    FluxoCaixa,
    RelatorioRentabilidade
)
from app.services.fluxo_caixa import FluxoCaixaService

router = APIRouter()

@router.get("/entradas", response_model=dict)
async def listar_entradas_estoque(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    produto_id: Optional[int] = Query(None, description="Filtrar por produto"),
    data_inicio: Optional[date] = Query(None, description="Data de início"),
    data_fim: Optional[date] = Query(None, description="Data de fim"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar entradas de estoque com filtros e paginação"""
    query = db.query(EntradaEstoque).options(joinedload(EntradaEstoque.produto))
    
    # Apply filters
    if produto_id:
        query = query.filter(EntradaEstoque.produto_id == produto_id)
    
    if data_inicio:
        query = query.filter(EntradaEstoque.data_entrada >= data_inicio)
    
    if data_fim:
        query = query.filter(EntradaEstoque.data_entrada <= data_fim)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by date
    entradas = query.order_by(desc(EntradaEstoque.data_entrada)).offset(skip).limit(limit).all()
    
    return {
        "data": {
            "items": [EntradaEstoqueSchema.from_orm(entrada) for entrada in entradas],
            "paginacao": {
                "pagina": (skip // limit) + 1,
                "itensPorPagina": limit,
                "totalItens": total,
                "totalPaginas": (total + limit - 1) // limit
            }
        },
        "message": "Entradas de estoque listadas com sucesso",
        "success": True
    }

@router.post("/entradas", response_model=dict)
async def criar_entrada_estoque(
    entrada_data: EntradaEstoqueCreate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Criar nova entrada de estoque (apenas administradores)"""
    # Verify product exists
    produto = db.query(Produto).filter(Produto.id == entrada_data.produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Create entrada
    db_entrada = EntradaEstoque(
        produto_id=entrada_data.produto_id,
        quantidade=entrada_data.quantidade,
        tipo_medida=entrada_data.tipo_medida,
        preco_custo=entrada_data.preco_custo,
        valor_total=entrada_data.preco_custo * entrada_data.quantidade,
        fornecedor=entrada_data.fornecedor,
        observacoes=entrada_data.observacoes
    )
    db.add(db_entrada)
    
    # Update or create inventory record
    inventario = db.query(Inventario).filter(Inventario.produto_id == entrada_data.produto_id).first()
    if inventario:
        inventario.quantidade_atual += entrada_data.quantidade
        inventario.data_ultima_atualizacao = datetime.utcnow()
    else:
        inventario = Inventario(
            produto_id=entrada_data.produto_id,
            quantidade_atual=entrada_data.quantidade,
            tipo_medida=entrada_data.tipo_medida,
            valor_unitario=entrada_data.preco_custo,
            valor_total=entrada_data.preco_custo * entrada_data.quantidade
        )
        db.add(inventario)
    
    db.commit()
    db.refresh(db_entrada)
    
    # Registrar no fluxo de caixa FIFO
    fluxo_service = FluxoCaixaService(db)
    fluxo_service.registrar_entrada_estoque(db_entrada)
    
    return {
        "data": EntradaEstoqueSchema.from_orm(db_entrada),
        "message": "Entrada de estoque criada com sucesso",
        "success": True
    }

@router.delete("/entradas/{entrada_id}", response_model=dict)
async def deletar_entrada_estoque(
    entrada_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deletar entrada de estoque (apenas administradores)"""
    from app.models.estoque import EstoqueFifo
    
    # Buscar a entrada
    entrada = db.query(EntradaEstoque).filter(EntradaEstoque.id == entrada_id).first()
    if not entrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de estoque não encontrada"
        )
    
    # Verificar se existem registros FIFO relacionados que foram usados em vendas
    # Como não temos quantidade_inicial no FIFO, vamos usar a quantidade da entrada original
    fifo_usados = db.query(EstoqueFifo).join(EntradaEstoque).filter(
        and_(
            EstoqueFifo.entrada_estoque_id == entrada_id,
            EstoqueFifo.quantidade_restante < EntradaEstoque.quantidade
        )
    ).first()
    
    if fifo_usados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar esta entrada pois ela já foi utilizada em vendas. Use ajuste de inventário para correções."
        )
    
    # Verificar inventário atual
    inventario = db.query(Inventario).filter(Inventario.produto_id == entrada.produto_id).first()
    if not inventario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventário do produto não encontrado"
        )
    
    # Verificar se há quantidade suficiente para remoção
    if inventario.quantidade_atual < entrada.quantidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quantidade insuficiente no inventário. Atual: {inventario.quantidade_atual}, Tentativa de remoção: {entrada.quantidade}"
        )
    
    # Remover registros FIFO não utilizados
    db.query(EstoqueFifo).filter(EstoqueFifo.entrada_estoque_id == entrada_id).delete()
    
    # Atualizar inventário
    inventario.quantidade_atual -= entrada.quantidade
    inventario.data_ultima_atualizacao = datetime.utcnow()
    
    # Se inventário ficar zerado e não há outras entradas, remover registro
    if inventario.quantidade_atual == 0:
        outras_entradas = db.query(EntradaEstoque).filter(
            and_(
                EntradaEstoque.produto_id == entrada.produto_id,
                EntradaEstoque.id != entrada_id
            )
        ).first()
        
        if not outras_entradas:
            db.delete(inventario)
    
    # Remover movimentação de caixa
    from app.models.estoque import MovimentacaoCaixa, TipoMovimentacao
    movimentacao = db.query(MovimentacaoCaixa).filter(
        and_(
            MovimentacaoCaixa.entrada_estoque_id == entrada_id,
            MovimentacaoCaixa.tipo_movimentacao == TipoMovimentacao.ENTRADA
        )
    ).first()
    
    if movimentacao:
        db.delete(movimentacao)
    
    # Salvar dados da entrada para resposta
    entrada_data = EntradaEstoqueSchema.from_orm(entrada)
    
    # Deletar a entrada
    db.delete(entrada)
    db.commit()
    
    return {
        "data": {
            "entrada_deletada": entrada_data,
            "inventario_atualizado": {
                "produto_id": inventario.produto_id if inventario in db else entrada.produto_id,
                "quantidade_anterior": entrada_data.quantidade + (inventario.quantidade_atual if inventario in db else 0),
                "quantidade_atual": inventario.quantidade_atual if inventario in db else 0,
                "quantidade_removida": entrada_data.quantidade
            }
        },
        "message": "Entrada de estoque deletada com sucesso",
        "success": True
    }

@router.get("/entradas/deletaveis", response_model=dict)
async def listar_entradas_deletaveis(
    produto_id: Optional[int] = Query(None, description="Filtrar por produto"),
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Listar entradas que podem ser deletadas (não utilizadas em vendas)"""
    from app.models.estoque import EstoqueFifo
    
    # Buscar entradas que não foram utilizadas em vendas
    query = db.query(EntradaEstoque).options(joinedload(EntradaEstoque.produto))
    
    if produto_id:
        query = query.filter(EntradaEstoque.produto_id == produto_id)
    
    # Subquery para entradas que têm FIFO utilizado (quantidade_restante < quantidade da entrada)
    subquery_fifo_utilizado = db.query(EstoqueFifo.entrada_estoque_id).join(EntradaEstoque).filter(
        EstoqueFifo.quantidade_restante < EntradaEstoque.quantidade
    ).subquery()
    
    entradas_deletaveis = query.filter(
        ~EntradaEstoque.id.in_(subquery_fifo_utilizado)
    ).order_by(desc(EntradaEstoque.data_entrada)).all()
    
    # Adicionar informações de status para cada entrada
    resultado = []
    for entrada in entradas_deletaveis:
        # Verificar se tem registros FIFO
        fifo_count = db.query(EstoqueFifo).filter(
            EstoqueFifo.entrada_estoque_id == entrada.id
        ).count()
        
        entrada_dict = EntradaEstoqueSchema.from_orm(entrada).dict()
        entrada_dict['status_exclusao'] = {
            'pode_deletar': True,
            'tem_fifo': fifo_count > 0,
            'motivo': 'Entrada não utilizada em vendas'
        }
        resultado.append(entrada_dict)
    
    return {
        "data": {
            "entradas_deletaveis": resultado,
            "total": len(resultado)
        },
        "message": f"{len(resultado)} entradas podem ser deletadas",
        "success": True
    }

@router.get("/entradas/{entrada_id}/status-exclusao", response_model=dict)
async def verificar_status_exclusao(
    entrada_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Verificar se uma entrada pode ser deletada e por quê"""
    from app.models.estoque import EstoqueFifo
    
    # Buscar a entrada
    entrada = db.query(EntradaEstoque).options(joinedload(EntradaEstoque.produto)).filter(
        EntradaEstoque.id == entrada_id
    ).first()
    
    if not entrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de estoque não encontrada"
        )
    
    # Verificar registros FIFO
    fifo_records = db.query(EstoqueFifo).filter(EstoqueFifo.entrada_estoque_id == entrada_id).all()
    
    pode_deletar = True
    motivos_bloqueio = []
    detalhes_fifo = []
    
    for fifo in fifo_records:
        # Buscar a entrada original para comparar quantidade
        entrada_original = db.query(EntradaEstoque).filter(EntradaEstoque.id == fifo.entrada_estoque_id).first()
        quantidade_inicial = entrada_original.quantidade if entrada_original else fifo.quantidade_restante
        quantidade_usada = quantidade_inicial - fifo.quantidade_restante
        
        detalhes_fifo.append({
            "quantidade_inicial": quantidade_inicial,
            "quantidade_restante": fifo.quantidade_restante,
            "quantidade_usada": quantidade_usada,
            "preco_custo": fifo.preco_custo_unitario
        })
        
        if quantidade_usada > 0:
            pode_deletar = False
            motivos_bloqueio.append(f"Quantidade {quantidade_usada} já foi utilizada em vendas")
    
    # Verificar inventário
    inventario = db.query(Inventario).filter(Inventario.produto_id == entrada.produto_id).first()
    
    status_inventario = {
        "quantidade_atual": inventario.quantidade_atual if inventario else 0,
        "quantidade_entrada": entrada.quantidade,
        "suficiente_para_remocao": inventario.quantidade_atual >= entrada.quantidade if inventario else False
    }
    
    if inventario and inventario.quantidade_atual < entrada.quantidade:
        pode_deletar = False
        motivos_bloqueio.append(f"Inventário atual ({inventario.quantidade_atual}) é menor que a quantidade da entrada ({entrada.quantidade})")
    
    return {
        "data": {
            "entrada": EntradaEstoqueSchema.from_orm(entrada),
            "pode_deletar": pode_deletar,
            "motivos_bloqueio": motivos_bloqueio,
            "detalhes_fifo": detalhes_fifo,
            "status_inventario": status_inventario,
            "impacto_exclusao": {
                "quantidade_removida": entrada.quantidade,
                "valor_removido": entrada.valor_total,
                "nova_quantidade_inventario": (inventario.quantidade_atual - entrada.quantidade) if inventario and pode_deletar else None
            }
        },
        "message": "Status de exclusão verificado com sucesso",
        "success": True
    }

@router.get("/inventario", response_model=dict)
async def listar_inventario(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    produto_id: Optional[int] = Query(None, description="Filtrar por produto"),
    estoque_baixo: Optional[bool] = Query(False, description="Mostrar apenas produtos com estoque baixo"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar inventário atual com filtros e paginação"""
    query = db.query(Inventario).options(joinedload(Inventario.produto))

    # Apply filters
    if produto_id:
        query = query.filter(Inventario.produto_id == produto_id)

    if estoque_baixo:
        # Só faz join uma vez!
        query = query.join(Produto).filter(
            Inventario.quantidade_atual < Produto.estoque_minimo
        )
        inventarios = query.order_by(Produto.nome).offset(skip).limit(limit).all()
    else:
        inventarios = query.join(Produto).order_by(Produto.nome).offset(skip).limit(limit).all()

    # Get total count
    total = query.count()

    return {
        "data": {
            "items": [InventarioSchema.from_orm(inventario) for inventario in inventarios],
            "paginacao": {
                "pagina": (skip // limit) + 1,
                "itensPorPagina": limit,
                "totalItens": total,
                "totalPaginas": (total + limit - 1) // limit
            }
        },
        "message": "Inventário listado com sucesso",
        "success": True
    }

@router.put("/inventario/{produto_id}", response_model=dict)
async def atualizar_inventario(
    produto_id: int,
    inventario_data: InventarioUpdate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Atualizar quantidade de inventário manualmente (apenas administradores) e recalcular valor_total pelo FIFO"""
    from app.models.estoque import EstoqueFifo

    # Verifica se o produto existe
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Busca ou cria o inventário
    inventario = db.query(Inventario).filter(Inventario.produto_id == produto_id).first()
    if not inventario:
        inventario = Inventario(produto_id=produto_id)
        db.add(inventario)
    
    # Atualiza inventário
    inventario.quantidade_atual = inventario_data.quantidade_atual
    inventario.observacoes = inventario_data.observacoes
    inventario.data_ultima_atualizacao = datetime.utcnow()

    # Recalcula valor_total pelo FIFO
    entradas_fifo = db.query(EstoqueFifo).filter(
        EstoqueFifo.produto_id == produto_id,
        EstoqueFifo.quantidade_restante > 0
    ).order_by(EstoqueFifo.id).all()

    quantidade_restante = inventario.quantidade_atual
    valor_total = 0

    for entrada in entradas_fifo:
        usar = min(entrada.quantidade_restante, quantidade_restante)
        valor_total += Decimal(usar) * Decimal(entrada.preco_custo_unitario)
        quantidade_restante -= usar
        if quantidade_restante <= 0:
            break

    inventario.valor_total = valor_total

    db.commit()
    db.refresh(inventario)
    
    return {
        "data": InventarioSchema.from_orm(inventario),
        "message": "Inventário atualizado com sucesso",
        "success": True
    }

@router.get("/consulta/{produto_id}", response_model=dict)
async def consultar_estoque_produto(
    produto_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Consultar estoque de um produto específico"""
    # Verify product exists
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Get inventory
    inventario = db.query(Inventario).filter(Inventario.produto_id == produto_id).first()
    
    # Get recent entries (last 10)
    entradas_recentes = db.query(EntradaEstoque).filter(
        EntradaEstoque.produto_id == produto_id
    ).order_by(desc(EntradaEstoque.data_entrada)).limit(10).all()
    
    # Calculate total entries in the last 30 days
    thirty_days_ago = datetime.utcnow().date().replace(day=1)  # Beginning of month
    total_entradas_mes = db.query(func.sum(EntradaEstoque.quantidade)).filter(
        and_(
            EntradaEstoque.produto_id == produto_id,
            EntradaEstoque.data_entrada >= thirty_days_ago
        )
    ).scalar() or 0
    
    consulta = EstoqueConsulta(
        produto=produto,
        quantidade_atual=inventario.quantidade_atual if inventario else 0,
        estoque_minimo=produto.estoque_minimo,
        estoque_baixo=inventario.quantidade_atual < produto.estoque_minimo if inventario else True,
        entradas_recentes=entradas_recentes,
        total_entradas_mes=total_entradas_mes,
        ultima_atualizacao=inventario.data_ultima_atualizacao if inventario else None
    )
    
    return {
        "data": consulta.dict(),
        "message": "Consulta de estoque realizada com sucesso",
        "success": True
    }

@router.get("/alertas", response_model=dict)
async def obter_alertas_estoque(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter produtos com estoque baixo"""
    # Get products with low stock
    produtos_estoque_baixo = db.query(Inventario).options(
        joinedload(Inventario.produto)
    ).join(Produto).filter(
        Inventario.quantidade_atual < Produto.estoque_minimo
    ).all()
    
    # Get products with no inventory record (assumed zero stock)
    produtos_sem_inventario = db.query(Produto).outerjoin(Inventario).filter(
        Inventario.id == None
    ).all()
    
    alertas = {
        "produtos_estoque_baixo": [
            {
                "produto": inventario.produto.nome,
                "produto_id": inventario.produto_id,
                "quantidade_atual": inventario.quantidade_atual,
                "estoque_minimo": inventario.produto.estoque_minimo
            }
            for inventario in produtos_estoque_baixo
        ],
        "produtos_sem_estoque": [
            {
                "produto": produto.nome,
                "produto_id": produto.id,
                "estoque_minimo": produto.estoque_minimo
            }
            for produto in produtos_sem_inventario
        ]
    }
    
    total_alertas = len(alertas["produtos_estoque_baixo"]) + len(alertas["produtos_sem_estoque"])
    
    return {
        "data": alertas,
        "total_alertas": total_alertas,
        "message": f"{total_alertas} alertas de estoque encontrados",
        "success": True
    }

@router.get("/fluxo-caixa", response_model=dict)
async def obter_fluxo_caixa(
    produto_id: Optional[int] = Query(None, description="Filtrar por produto"),
    data_inicio: Optional[date] = Query(None, description="Data de início"),
    data_fim: Optional[date] = Query(None, description="Data de fim"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter relatório de fluxo de caixa com controle FIFO"""
    fluxo_service = FluxoCaixaService(db)
    
    # Converter dates para datetime se necessário
    data_inicio_dt = datetime.combine(data_inicio, datetime.min.time()) if data_inicio else None
    data_fim_dt = datetime.combine(data_fim, datetime.max.time()) if data_fim else None
    
    relatorio = fluxo_service.obter_relatorio_fluxo_caixa(
        produto_id=produto_id,
        data_inicio=data_inicio_dt,
        data_fim=data_fim_dt
    )
    
    movimentacoes_ordenadas = sorted(
        relatorio["movimentacoes"],
        key=lambda mov: mov.data_movimentacao,
        reverse=True
    )

    return {
        "data": {
            "total_entradas": relatorio["total_entradas"],
            "total_saidas": relatorio["total_saidas"],
            "saldo": relatorio["saldo"],
            "lucro_bruto_total": relatorio["lucro_bruto_total"],
            "margem_media": relatorio["margem_media"],
            "quantidade_vendas": relatorio["quantidade_vendas"],
            "movimentacoes": [
                {
                    "id": mov.id,
                    "produto_id": mov.produto_id,
                    "tipo": mov.tipo_movimentacao.value,
                    "quantidade": mov.quantidade,
                    "preco_unitario": mov.preco_unitario,
                    "valor_total": mov.valor_total,
                    "data": mov.data_movimentacao,
                    "observacoes": mov.observacoes
                }
                for mov in movimentacoes_ordenadas
            ]
        },
        "message": "Relatório de fluxo de caixa gerado com sucesso",
        "success": True
    }

@router.get("/rentabilidade", response_model=dict)
async def obter_rentabilidade(
    data_inicio: date = Query(..., description="Data de início (obrigatório)"),
    data_fim: date = Query(..., description="Data de fim (obrigatório)"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter relatório de rentabilidade por período"""
    from app.models.estoque import LucroBruto, MovimentacaoCaixa, TipoMovimentacao
    
    data_inicio_dt = datetime.combine(data_inicio, datetime.min.time())
    data_fim_dt = datetime.combine(data_fim, datetime.max.time())
    
    # Buscar lucros brutos do período
    lucros = db.query(LucroBruto).filter(
        and_(
            LucroBruto.data_calculo >= data_inicio_dt,
            LucroBruto.data_calculo <= data_fim_dt
        )
    ).all()
    
    # Agrupar por produto
    produtos_rentabilidade = {}
    for lucro in lucros:
        produto_id = lucro.produto_id
        if produto_id not in produtos_rentabilidade:
            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            produtos_rentabilidade[produto_id] = {
                "produto": {
                    "id": produto.id,
                    "nome": produto.nome,
                    "descricao": produto.descricao
                },
                "quantidade_vendida": Decimal('0'),
                "receita_total": Decimal('0'),
                "custo_total": Decimal('0'),
                "lucro_bruto": Decimal('0'),
                "vendas": 0
            }
        
        dados = produtos_rentabilidade[produto_id]
        dados["quantidade_vendida"] += lucro.quantidade_vendida
        dados["receita_total"] += lucro.receita_total
        dados["custo_total"] += lucro.custo_total
        dados["lucro_bruto"] += lucro.lucro_bruto
        dados["vendas"] += 1
    
    # Calcular margens
    for dados in produtos_rentabilidade.values():
        if dados["receita_total"] > 0:
            dados["margem_bruta"] = (dados["lucro_bruto"] / dados["receita_total"]) * 100
        else:
            dados["margem_bruta"] = Decimal('0')
    
    # Totais gerais
    total_vendas = sum(p["receita_total"] for p in produtos_rentabilidade.values())
    total_custos = sum(p["custo_total"] for p in produtos_rentabilidade.values())
    lucro_bruto_total = total_vendas - total_custos
    margem_bruta_geral = (lucro_bruto_total / total_vendas * 100) if total_vendas > 0 else Decimal('0')
    
    return {
        "data": {
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            },
            "resumo": {
                "total_vendas": total_vendas,
                "total_custos": total_custos,
                "lucro_bruto_total": lucro_bruto_total,
                "margem_bruta_geral": margem_bruta_geral,
                "produtos_vendidos": len(produtos_rentabilidade)
            },
            "produtos": list(produtos_rentabilidade.values())
        },
        "message": "Relatório de rentabilidade gerado com sucesso",
        "success": True
    }
