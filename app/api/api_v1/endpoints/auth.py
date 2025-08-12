from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.usuario import Login, LoginResponse, Usuario as UsuarioSchema

router = APIRouter()

@router.post("/login", response_model=dict)
async def login(login_data: Login, db: Session = Depends(get_db)):
    """Login endpoint"""
    # Find user by email
    user = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    if not user or not verify_password(login_data.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    
    return {
        "data": {
            "user": UsuarioSchema.from_orm(user),
            "token": access_token
        },
        "message": "Login realizado com sucesso",
        "success": True
    }

@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {
        "message": "Logout realizado com sucesso",
        "success": True
    }

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """Get current user information"""
    return {
        "data": UsuarioSchema.from_orm(current_user),
        "message": "Usuário obtido com sucesso",
        "success": True
    }
