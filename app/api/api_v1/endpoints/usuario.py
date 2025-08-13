#faça os imports
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.deps import get_current_user, get_current_admin_user
from app.models.usuario import Usuario
from app.schemas.usuario import Login, LoginResponse, Usuario as UsuarioSchema, UsuarioBase, TipoUsuario, FuncionarioCreate
from typing import Optional


router = APIRouter()
#usar FuncionarioCreate

#mandar sempre um email diferente
@router.post("/funcionarios", response_model=dict)
async def criar_funcionario(
    funcionario: FuncionarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin_user)
):
    """Cria um novo funcionário"""
    # Verifica se já existe um usuário com o mesmo CPF/CNPJ ou email
    usuario_existente = db.query(Usuario).filter(
        (Usuario.cpf_ou_cnpj == funcionario.cpf_ou_cnpj)
    ).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário com este CPF/CNPJ já existe"
        )

    # Cria o hash da senha padrão
    senha_hash = get_password_hash("func123")

    email = getattr(funcionario, "email", None)
    novo_usuario = Usuario(
        nome=funcionario.nome,
        cpf_ou_cnpj=funcionario.cpf_ou_cnpj,
        email=email,
        senha_hash=senha_hash,
        tipo=TipoUsuario.FUNCIONARIO,
        ativo=True
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # Se o email não for enviado, gera um email único baseado no CPF/CNPJ
    if not email:
        email = f"funcionario_{funcionario.cpf_ou_cnpj}@exemplo.com"
        novo_usuario.email = email
        db.commit()
        db.refresh(novo_usuario)

    return {
        "data": {
            "id": novo_usuario.id,
            "nome": novo_usuario.nome,
            "cpf_ou_cnpj": novo_usuario.cpf_ou_cnpj,
            "email": novo_usuario.email,
            "tipo": novo_usuario.tipo,
        },
        "message": "Funcionário cadastrado com sucesso",
        "success": True
    }

# endpoint para alterar senha
@router.put("/funcionarios/{funcionario_id}/senha", response_model=dict)
async def alterar_senha_funcionario(
    funcionario_id: int,
    nova_senha: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Altera a senha de um funcionário (apenas o próprio funcionário pode alterar)"""
    if current_user.id != funcionario_id or current_user.tipo != TipoUsuario.FUNCIONARIO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar sua própria senha"
        )

    funcionario = db.query(Usuario).filter(Usuario.id == funcionario_id, Usuario.tipo == TipoUsuario.FUNCIONARIO).first()
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )

    funcionario.senha_hash = get_password_hash(nova_senha)
    db.commit()

    return {
        "data": {
            "id": funcionario.id,
            "nome": funcionario.nome,
            "cpf_ou_cnpj": funcionario.cpf_ou_cnpj,
            "tipo": funcionario.tipo,
        },
        "message": "Senha alterada com sucesso",
        "success": True
    }
#alterar senha de administrador
@router.put("/administradores/{admin_id}/senha", response_model=dict)
async def alterar_senha_administrador(
    admin_id: int,
    nova_senha: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin_user)
):
    """Altera a senha de um administrador"""
    administrador = db.query(Usuario).filter(Usuario.id == admin_id, Usuario.tipo == TipoUsuario.ADMINISTRADOR).first()
    if not administrador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrador não encontrado"
        )

    administrador.senha_hash = get_password_hash(nova_senha)
    db.commit()

    return {
        "data": {
            "id": administrador.id,
            "nome": administrador.nome,
            "cpf_ou_cnpj": administrador.cpf_ou_cnpj,
            "email": administrador.email,
            "tipo": administrador.tipo,
        },
        "message": "Senha alterada com sucesso",
        "success": True
    }


@router.put("/funcionarios/{funcionario_id}/nome", response_model=dict)
async def alterar_nome_funcionario(
    funcionario_id: int,
    novo_nome: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin_user)
):
    """Altera o nome de um funcionário"""
    funcionario = db.query(Usuario).filter(Usuario.id == funcionario_id).first()
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )

    funcionario.nome = novo_nome
    db.commit()

    return {
        "data": {
            "id": funcionario.id,
            "nome": funcionario.nome,
            "cpf_ou_cnpj": funcionario.cpf_ou_cnpj,
            "email": funcionario.email,
            "tipo": funcionario.tipo,
        },
        "message": "Nome alterado com sucesso",
        "success": True
    }

# Atualizar coluna ativo do funcionario para 1 ou 0
@router.put("/funcionarios/{funcionario_id}/ativo", response_model=dict)
async def atualizar_ativo_funcionario(
    funcionario_id: int,
    ativo: bool,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin_user)
):
    """Atualiza a coluna ativo de um funcionário"""
    funcionario = db.query(Usuario).filter(Usuario.id == funcionario_id).first()
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )

    funcionario.ativo = ativo
    db.commit()

    return {
        "data": {
            "id": funcionario.id,
            "nome": funcionario.nome,
            "cpf_ou_cnpj": funcionario.cpf_ou_cnpj,
            "email": funcionario.email,
            "tipo": funcionario.tipo,
            "ativo": funcionario.ativo,
        },
        "message": "Status do funcionário atualizado com sucesso",
        "success": True
    }

@router.delete("/funcionarios/{funcionario_id}", response_model=dict)
async def deletar_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin_user)
):
    """Deleta um funcionário"""
    funcionario = db.query(Usuario).filter(Usuario.id == funcionario_id).first()
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )

    db.delete(funcionario)
    db.commit()

    return {
        "data": {
            "id": funcionario.id,
            "nome": funcionario.nome,
            "cpf_ou_cnpj": funcionario.cpf_ou_cnpj,
            "email": funcionario.email,
            "tipo": funcionario.tipo,
        },
        "message": "Funcionário deletado com sucesso",
        "success": True
    }
