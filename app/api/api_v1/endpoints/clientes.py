from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente import Cliente as ClienteSchema, ClienteCreate, ClienteUpdate

router = APIRouter()

@router.get("/", response_model=dict)
async def listar_clientes(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    cpf_ou_cnpj: Optional[str] = Query(None, description="Filtrar por CPF/CNPJ"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar clientes com filtros e paginação"""
    query = db.query(Cliente)
    
    # Apply filters
    if nome:
        query = query.filter(
            or_(
                Cliente.nome.ilike(f"%{nome}%"),
                Cliente.nome_fantasia.ilike(f"%{nome}%")
            )
        )
    
    if cpf_ou_cnpj:
        query = query.filter(Cliente.cpf_ou_cnpj.ilike(f"%{cpf_ou_cnpj}%"))
    
    if ativo is not None:
        query = query.filter(Cliente.ativo == ativo)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    clientes = query.offset(skip).limit(limit).all()
    
    return {
        "data": {
            "items": [ClienteSchema.from_orm(cliente) for cliente in clientes],
            "paginacao": {
                "pagina": (skip // limit) + 1,
                "itensPorPagina": limit,
                "totalItens": total,
                "totalPaginas": (total + limit - 1) // limit
            }
        },
        "message": "Clientes listados com sucesso",
        "success": True
    }

@router.get("/{cliente_id}", response_model=dict)
async def obter_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter cliente por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return {
        "data": ClienteSchema.from_orm(cliente),
        "message": "Cliente obtido com sucesso",
        "success": True
    }

@router.post("/", response_model=dict)
async def criar_cliente(
    cliente_data: ClienteCreate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Criar novo cliente (apenas administradores)"""
    # Check if CPF/CNPJ already exists
    existing_cliente = db.query(Cliente).filter(
        Cliente.cpf_ou_cnpj == cliente_data.cpf_ou_cnpj
    ).first()
    
    if existing_cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF/CNPJ já cadastrado"
        )
    
    # Create new cliente
    db_cliente = Cliente(**cliente_data.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    
    return {
        "data": ClienteSchema.from_orm(db_cliente),
        "message": "Cliente criado com sucesso",
        "success": True
    }

@router.put("/{cliente_id}", response_model=dict)
async def atualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Atualizar cliente (apenas administradores)"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Check if new CPF/CNPJ already exists (if provided)
    if cliente_data.cpf_ou_cnpj and cliente_data.cpf_ou_cnpj != cliente.cpf_ou_cnpj:
        existing_cliente = db.query(Cliente).filter(
            Cliente.cpf_ou_cnpj == cliente_data.cpf_ou_cnpj,
            Cliente.id != cliente_id
        ).first()
        
        if existing_cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF/CNPJ já cadastrado para outro cliente"
            )
    
    # Update cliente
    update_data = cliente_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)
    
    db.commit()
    db.refresh(cliente)
    
    return {
        "data": ClienteSchema.from_orm(cliente),
        "message": "Cliente atualizado com sucesso",
        "success": True
    }

@router.delete("/{cliente_id}", response_model=dict)
async def excluir_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Excluir cliente (apenas administradores)"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    db.delete(cliente)
    db.commit()
    
    return {
        "message": "Cliente excluído com sucesso",
        "success": True
    }
