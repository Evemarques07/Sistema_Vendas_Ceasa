import os
from fastapi.responses import FileResponse
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.produto import Produto as ProdutoSchema, ProdutoCreate, ProdutoUpdate
from app.utils.upload import process_and_upload_image, delete_image_from_gdrive

PASTA_IMAGENS = "public"
router = APIRouter()

@router.get("/", response_model=dict)
async def listar_produtos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar produtos com filtros e paginação"""
    query = db.query(Produto)
    
    # Filtrar por nome
    if nome:
        query = query.filter(Produto.nome.ilike(f"%{nome}%"))
    
    if ativo is not None:
        query = query.filter(Produto.ativo == ativo)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    produtos = query.offset(skip).limit(limit).all()
    
    return {
        "data": {
            "items": [ProdutoSchema.from_orm(produto) for produto in produtos],
            "paginacao": {
                "pagina": (skip // limit) + 1,
                "itensPorPagina": limit,
                "totalItens": total,
                "totalPaginas": (total + limit - 1) // limit
            }
        },
        "message": "Produtos listados com sucesso",
        "success": True
    }

@router.get("/{produto_id}", response_model=dict)
async def obter_produto(
    produto_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter produto por ID"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    return {
        "data": ProdutoSchema.from_orm(produto),
        "message": "Produto obtido com sucesso",
        "success": True
    }

@router.post("/", response_model=dict)
async def criar_produto(
    produto: ProdutoCreate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Criar novo produto (apenas administradores)"""
    # Check if produto already exists by nome
    existing_produto = db.query(Produto).filter(
        Produto.nome.ilike(produto.nome)
    ).first()
    
    if existing_produto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto com este nome já existe"
        )
    
    # Create new produto
    db_produto = Produto(
        nome=produto.nome,
        descricao=produto.descricao,
        preco_venda=produto.preco_venda,
        tipo_medida=produto.tipo_medida,
        estoque_minimo=produto.estoque_minimo,
        ativo=produto.ativo if hasattr(produto, 'ativo') else True,
        imagem=getattr(produto, 'imagem', None)
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    
    return {
        "data": ProdutoSchema.from_orm(db_produto),
        "message": "Produto criado com sucesso",
        "success": True
    }

@router.put("/{produto_id}", response_model=dict)
async def atualizar_produto(
    produto_id: int,
    produto_update: ProdutoUpdate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Atualizar produto (apenas administradores)"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Check if new nome already exists (if provided)
    if produto_update.nome and produto_update.nome != produto.nome:
        existing_produto = db.query(Produto).filter(
            Produto.nome.ilike(produto_update.nome),
            Produto.id != produto_id
        ).first()
        
        if existing_produto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Produto com este nome já existe"
            )
    
    # Update fields if provided
    update_data = produto_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(produto, field, value)
    
    db.commit()
    db.refresh(produto)
    
    return {
        "data": ProdutoSchema.from_orm(produto),
        "message": "Produto atualizado com sucesso",
        "success": True
    }

@router.put("/{produto_id}/imagem", response_model=dict)
async def atualizar_imagem_produto(
    produto_id: int,
    imagem_url: str,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Atualizar apenas a URL da imagem do produto (apenas administradores)"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    # Atualiza a URL da imagem
    produto.imagem = imagem_url
    db.commit()
    db.refresh(produto)
    return {
        "data": ProdutoSchema.from_orm(produto),
        "message": "Imagem do produto atualizada com sucesso",
        "success": True
    }

@router.delete("/{produto_id}", response_model=dict)
async def excluir_produto(
    produto_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Excluir produto (apenas administradores)"""
    from app.models.estoque import EntradaEstoque, Inventario, EstoqueFifo, MovimentacaoCaixa, LucroBruto
    from app.models.venda import ItemVenda
    
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Verificar se o produto possui dependências
    dependencies = []
    
    # Verificar entradas de estoque
    entradas_count = db.query(EntradaEstoque).filter(EntradaEstoque.produto_id == produto_id).count()
    if entradas_count > 0:
        dependencies.append(f"entradas de estoque ({entradas_count})")
    
    # Verificar itens de venda
    itens_venda_count = db.query(ItemVenda).filter(ItemVenda.produto_id == produto_id).count()
    if itens_venda_count > 0:
        dependencies.append(f"itens de venda ({itens_venda_count})")
    
    # Verificar inventário
    inventario_count = db.query(Inventario).filter(Inventario.produto_id == produto_id).count()
    if inventario_count > 0:
        dependencies.append(f"registros de inventário ({inventario_count})")
    
    # Verificar estoque FIFO
    fifo_count = db.query(EstoqueFifo).filter(EstoqueFifo.produto_id == produto_id).count()
    if fifo_count > 0:
        dependencies.append(f"registros FIFO ({fifo_count})")
    
    # Verificar movimentações de caixa
    movimentacoes_count = db.query(MovimentacaoCaixa).filter(MovimentacaoCaixa.produto_id == produto_id).count()
    if movimentacoes_count > 0:
        dependencies.append(f"movimentações de caixa ({movimentacoes_count})")
    
    # Verificar lucros brutos
    lucros_count = db.query(LucroBruto).filter(LucroBruto.produto_id == produto_id).count()
    if lucros_count > 0:
        dependencies.append(f"registros de lucro ({lucros_count})")
    
    # Se houver dependências, retornar erro informativo
    if dependencies:
        dependencies_text = ", ".join(dependencies)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir o produto pois ele possui: {dependencies_text}. Para excluir o produto, primeiro remova todos os registros relacionados ou desative o produto."
        )
    
    # Delete image from Google Drive if exists
    if produto.imagem:
        delete_image_from_gdrive(produto.imagem)
    
    db.delete(produto)
    db.commit()
    
    return {
        "message": "Produto excluído com sucesso",
        "success": True
    }

@router.post("/imagem/", response_model=dict)
async def upload_imagem_produto(
    produto_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_admin_user)
):
    """Faz upload de uma imagem para um produto e salva em /public/{produto_id}.ext"""
    extensao = os.path.splitext(file.filename)[1].lower()
    if extensao not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Formato de imagem não suportado.")
    if not os.path.exists(PASTA_IMAGENS):
        os.makedirs(PASTA_IMAGENS)
    caminho = os.path.join(PASTA_IMAGENS, f"{produto_id}{extensao}")
    with open(caminho, "wb") as buffer:
        buffer.write(await file.read())
    return {
        "message": "Imagem enviada com sucesso",
        "filename": f"{produto_id}{extensao}",
        "success": True
    }

@router.get("/imagem/{produto_id}")
async def get_imagem_produto(produto_id: int):
    """Retorna a imagem do produto salva em /public/{produto_id}.ext"""
    for ext in [".jpg", ".jpeg", ".png"]:
        caminho = os.path.join(PASTA_IMAGENS, f"{produto_id}{ext}")
        if os.path.exists(caminho):
            return FileResponse(caminho, media_type=f"image/{ext.replace('.', '')}")
    raise HTTPException(status_code=404, detail="Imagem não encontrada")

@router.get("/imagens/listar", response_model=dict, dependencies=[])
async def listar_imagens():
    """Lista todas as imagens de produtos na pasta /public"""
    if not os.path.exists(PASTA_IMAGENS):
        return {"data": [], "message": "Nenhuma imagem encontrada", "success": True}
    arquivos = [f for f in os.listdir(PASTA_IMAGENS) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    return {"data": arquivos, "message": "Imagens listadas com sucesso", "success": True}

@router.delete("/imagem/{produto_id}", response_model=dict)
async def deletar_imagem_produto(produto_id: int, current_user: Usuario = Depends(get_current_admin_user)):
    """Deleta a imagem do produto na pasta /public/{produto_id}.ext"""
    for ext in [".jpg", ".jpeg", ".png"]:
        caminho = os.path.join(PASTA_IMAGENS, f"{produto_id}{ext}")
        if os.path.exists(caminho):
            os.remove(caminho)
            return {"message": "Imagem deletada com sucesso", "success": True}
    raise HTTPException(status_code=404, detail="Imagem não encontrada")