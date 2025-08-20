from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from decimal import Decimal

from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.venda import Venda, ItemVenda
from app.core.enums import SituacaoPedido, SituacaoPagamento
from app.models.estoque import LucroBruto, MovimentacaoCaixa
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.models.estoque import Inventario
from app.utils.timezone import now_brazil, start_of_day_brazil, end_of_day_brazil, format_brazil_datetime
from app.schemas.venda import (
    Venda as VendaSchema, 
    VendaCreate, 
    VendaUpdate,
    SeparacaoUpdate
)
from app.services.fluxo_caixa import FluxoCaixaService

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
    
    # === VENDAS DO PERÍODO ===
    
    # Vendas de hoje / período
    vendas_periodo = vendas_periodo_query.all()
    
    # Separar por situação
    vendas_em_separacao = [v for v in vendas_periodo if v.situacao_pedido == SituacaoPedido.A_SEPARAR]
    vendas_separadas = [v for v in vendas_periodo if v.situacao_pedido == SituacaoPedido.SEPARADO]
    
    # Calcular totais
    total_vendas_periodo = sum(float(v.total_venda) for v in vendas_periodo)
    total_em_separacao = sum(float(v.total_venda) for v in vendas_em_separacao)
    total_separadas = sum(float(v.total_venda) for v in vendas_separadas)
    
    # === ESTATÍSTICAS DE CLIENTES ===
    
    # Total de clientes
    total_clientes = db.query(Cliente).count()
    
    # Clientes ativos
    total_clientes_ativos = db.query(Cliente).filter(Cliente.ativo == True).count()
    
    # === VENDAS MENSAIS ===
    
    # Mês atual
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    vendas_mes_atual = db.query(func.count(Venda.id), func.sum(Venda.total_venda)).filter(
        and_(
            extract('month', Venda.data_venda) == mes_atual,
            extract('year', Venda.data_venda) == ano_atual
        )
    ).first()
    
    # Mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
    
    vendas_mes_anterior = db.query(func.count(Venda.id), func.sum(Venda.total_venda)).filter(
        and_(
            extract('month', Venda.data_venda) == mes_anterior,
            extract('year', Venda.data_venda) == ano_anterior
        )
    ).first()
    
    # === PAGAMENTOS PENDENTES ===
    
    vendas_pendentes = db.query(Venda).filter(
        Venda.situacao_pagamento == SituacaoPagamento.PENDENTE
    ).all()
    
    total_pagamentos_pendentes = sum(float(v.total_venda) for v in vendas_pendentes)
    
    # === MONTAR RESPOSTA ===
    
    dashboard = {
        "periodo": {
            "data_inicio": data_inicio_dt.strftime("%Y-%m-%d"),
            "data_fim": data_fim_dt.strftime("%Y-%m-%d"),
            "descricao": periodo_texto
        },
        "vendas_periodo": {
            "total_vendas": len(vendas_periodo),
            "valor_total": total_vendas_periodo,
            "em_separacao": {
                "quantidade": len(vendas_em_separacao),
                "valor": total_em_separacao,
                "vendas": [
                    {
                        "id": v.id,
                        "cliente": v.cliente.nome if v.cliente else "Cliente não encontrado",
                        "valor": float(v.total_venda),
                        "data_venda": v.data_venda.strftime("%Y-%m-%d %H:%M:%S")
                    } for v in vendas_em_separacao
                ]
            },
            "separadas": {
                "quantidade": len(vendas_separadas),
                "valor": total_separadas,
                "vendas": [
                    {
                        "id": v.id,
                        "cliente": v.cliente.nome if v.cliente else "Cliente não encontrado",
                        "valor": float(v.total_venda),
                        "data_venda": v.data_venda.strftime("%Y-%m-%d %H:%M:%S"),
                        "data_separacao": v.data_separacao.strftime("%Y-%m-%d %H:%M:%S") if v.data_separacao else None
                    } for v in vendas_separadas
                ]
            }
        },
        "estatisticas_clientes": {
            "total_clientes": total_clientes,
            "clientes_ativos": total_clientes_ativos,
            "clientes_inativos": total_clientes - total_clientes_ativos
        },
        "vendas_mensais": {
            "mes_atual": {
                "mes": mes_atual,
                "ano": ano_atual,
                "quantidade": vendas_mes_atual[0] or 0,
                "valor_total": float(vendas_mes_atual[1] or 0)
            },
            "mes_anterior": {
                "mes": mes_anterior,
                "ano": ano_anterior,
                "quantidade": vendas_mes_anterior[0] or 0,
                "valor_total": float(vendas_mes_anterior[1] or 0)
            },
            "comparacao": {
                "diferenca_quantidade": (vendas_mes_atual[0] or 0) - (vendas_mes_anterior[0] or 0),
                "diferenca_valor": float((vendas_mes_atual[1] or 0) - (vendas_mes_anterior[1] or 0)),
                "crescimento_percentual": round(
                    ((vendas_mes_atual[1] or 0) - (vendas_mes_anterior[1] or 0)) / (vendas_mes_anterior[1] or 1) * 100, 2
                ) if vendas_mes_anterior[1] else 0
            }
        },
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
        }
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
    
    # Create venda
    db_venda = Venda(
        cliente_id=venda_data.cliente_id,
        total_venda=total_venda,
        observacoes=venda_data.observacoes
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

@router.post("/venda-rapida", response_model=dict)
async def venda_rapida(
    produtos: list = Body(..., example=[
        {"produto_id": 1, "quantidade": 2.5, "tipo_medida": "KG"},
        {"produto_id": 2, "quantidade": 1, "tipo_medida": "UNIDADE"}
    ]),
    cliente_id: Optional[int] = Body(None, description="ID do cliente (opcional)"),
    observacoes: Optional[str] = Body(None),
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Realiza uma venda rápida (balcão), podendo ou não identificar o cliente.
    Deduz do estoque e faz os cálculos FIFO normalmente.
    """
    total_venda = Decimal('0.00')
    itens_venda = []

    # Verifica cliente se informado
    cliente = None
    if cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )

    # Verifica produtos e estoque
    for item in produtos:
        produto = db.query(Produto).filter(Produto.id == item["produto_id"]).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item['produto_id']} não encontrado"
            )
        inventario = db.query(Inventario).filter(Inventario.produto_id == produto.id).first()
        if not inventario or inventario.quantidade_atual < Decimal(str(item["quantidade"])):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto '{produto.nome}'"
            )
        valor_unitario = produto.preco_venda
        valor_total = Decimal(str(item["quantidade"])) * valor_unitario
        total_venda += valor_total
        itens_venda.append({
            "produto_id": produto.id,
            "quantidade": Decimal(str(item["quantidade"])),
            "tipo_medida": item["tipo_medida"],
            "valor_unitario": valor_unitario,
            "valor_total_produto": valor_total
        })

    # Cria a venda
    db_venda = Venda(
        cliente_id=cliente.id if cliente else None,
        total_venda=total_venda,
        observacoes=observacoes
    )
    db.add(db_venda)
    db.flush()  # Para pegar o ID

    # Cria os itens da venda e deduz do estoque
    for item in itens_venda:
        db_item = ItemVenda(
            venda_id=db_venda.id,
            produto_id=item["produto_id"],
            quantidade=item["quantidade"],
            tipo_medida=item["tipo_medida"],
            valor_unitario=item["valor_unitario"],
            valor_total_produto=item["valor_total_produto"],
            quantidade_real=item["quantidade"]
        )
        db.add(db_item)
        # Diminui do estoque
        inventario = db.query(Inventario).filter(Inventario.produto_id == item["produto_id"]).first()
        inventario.quantidade_atual -= item["quantidade"]
        inventario.data_ultima_atualizacao = now_brazil()

    # Marca venda como separada e paga (venda balcão)
    db_venda.situacao_pedido = SituacaoPedido.SEPARADO
    db_venda.situacao_pagamento = SituacaoPagamento.PAGO
    db_venda.funcionario_separacao_id = current_user.id
    db_venda.data_separacao = now_brazil()

    db.commit()
    db.refresh(db_venda)

    # Processa FIFO e lucro bruto
    fluxo_service = FluxoCaixaService(db)
    fluxo_service.processar_venda_separada(db_venda)

    return {
        "data": VendaSchema.from_orm(db_venda),
        "message": "Venda rápida realizada com sucesso",
        "success": True
    }

@router.put("/{venda_id}/separacao", response_model=dict)
async def atualizar_separacao(
    venda_id: int,
    separacao_data: SeparacaoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar separação de produtos - Diminui do estoque"""
    venda = db.query(Venda).filter(Venda.id == venda_id).first()
    if not venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Verificar se a venda ainda não foi separada
    if venda.situacao_pedido == SituacaoPedido.SEPARADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta venda já foi separada anteriormente"
        )
    
    # Primeiro, verificar se há estoque suficiente para todos os produtos
    produtos_com_estoque_insuficiente = []
    
    for produto_separado in separacao_data.produtos_separados:
        produto_id = produto_separado.produto_id if hasattr(produto_separado, 'produto_id') else produto_separado["produto_id"]
        quantidade_real = Decimal(str(produto_separado.quantidade_real if hasattr(produto_separado, 'quantidade_real') else produto_separado["quantidade_real"]))
        
        # Verificar se o produto existe no pedido
        item = db.query(ItemVenda).filter(
            ItemVenda.venda_id == venda_id,
            ItemVenda.produto_id == produto_id
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto ID {produto_id} não encontrado nesta venda"
            )
        
        # Verificar estoque disponível
        inventario = db.query(Inventario).filter(
            Inventario.produto_id == produto_id
        ).first()
        
        if not inventario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto '{item.produto.nome}' não possui estoque cadastrado"
            )
        
        if inventario.quantidade_atual < quantidade_real:
            produtos_com_estoque_insuficiente.append({
                "produto_nome": item.produto.nome,
                "quantidade_solicitada": float(quantidade_real),
                "quantidade_disponivel": float(inventario.quantidade_atual)
            })
    
    # Se algum produto não tem estoque suficiente, retornar erro
    if produtos_com_estoque_insuficiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Estoque insuficiente para os seguintes produtos:",
                "produtos": produtos_com_estoque_insuficiente
            }
        )
    
    # Se chegou até aqui, todos os produtos têm estoque suficiente
    # Agora atualizar os itens e diminuir o estoque
    novo_total = Decimal('0.00')
    
    for produto_separado in separacao_data.produtos_separados:
        produto_id = produto_separado.produto_id if hasattr(produto_separado, 'produto_id') else produto_separado["produto_id"]
        quantidade_real = Decimal(str(produto_separado.quantidade_real if hasattr(produto_separado, 'quantidade_real') else produto_separado["quantidade_real"]))
        
        # Atualizar item da venda
        item = db.query(ItemVenda).filter(
            ItemVenda.venda_id == venda_id,
            ItemVenda.produto_id == produto_id
        ).first()
        
        item.quantidade_real = quantidade_real
        item.valor_total_produto = quantidade_real * item.valor_unitario
        novo_total += item.valor_total_produto
        
        # Diminuir do estoque
        inventario = db.query(Inventario).filter(
            Inventario.produto_id == produto_id
        ).first()
        
        inventario.quantidade_atual -= quantidade_real
        from datetime import datetime
        inventario.data_ultima_atualizacao = now_brazil()
    
    # Atualizar venda com informações de separação
    venda.total_venda = novo_total
    venda.situacao_pedido = SituacaoPedido.SEPARADO
    venda.funcionario_separacao_id = current_user.id
    venda.data_separacao = now_brazil()
    
    db.commit()
    db.refresh(venda)
    
    # Processar no fluxo de caixa FIFO
    fluxo_service = FluxoCaixaService(db)
    lucros_gerados = fluxo_service.processar_venda_separada(venda)
    
    return {
        "data": VendaSchema.from_orm(venda),
        "message": "Separação atualizada com sucesso. Estoque diminuído automaticamente.",
        "success": True
    }

@router.put("/{venda_id}/cancelar-separacao", response_model=dict)
async def cancelar_separacao(
    venda_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancelar separação - Retorna produtos ao estoque"""
    venda = db.query(Venda).filter(Venda.id == venda_id).first()
    if not venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Verificar se a venda está separada
    if venda.situacao_pedido != SituacaoPedido.SEPARADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta venda não está separada"
        )
    
    # Verificar se ainda não foi paga
    if venda.situacao_pagamento == SituacaoPagamento.PAGO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar separação de venda já paga"
        )
    
    # Retornar produtos ao estoque
    novo_total = Decimal('0.00')
    itens = db.query(ItemVenda).filter(ItemVenda.venda_id == venda_id).all()
    
    for item in itens:
        if item.quantidade_real:
            # Retornar quantidade ao estoque
            inventario = db.query(Inventario).filter(
                Inventario.produto_id == item.produto_id
            ).first()
            
            if inventario:
                inventario.quantidade_atual += item.quantidade_real
                from datetime import datetime
                inventario.data_ultima_atualizacao = now_brazil()
            
            # Resetar quantidade real
            item.quantidade_real = None
            item.valor_total_produto = item.quantidade * item.valor_unitario
            novo_total += item.valor_total_produto
    
    # Atualizar venda - limpar informações de separação
    venda.total_venda = novo_total
    venda.situacao_pedido = SituacaoPedido.A_SEPARAR
    venda.funcionario_separacao_id = None
    venda.data_separacao = None
    
    db.commit()
    db.refresh(venda)
    
    return {
        "data": VendaSchema.from_orm(venda),
        "message": "Separação cancelada com sucesso. Produtos retornados ao estoque.",
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
    if (datetime.utcnow() - venda.data_venda).total_seconds() > 86400:
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