"""
Endpoint para informações do sistema e timezone
"""

from fastapi import APIRouter
from app.utils.timezone import get_brazil_timezone_info, now_brazil, now_utc

router = APIRouter()

@router.get("/timezone-info")
async def get_timezone_info():
    """
    Retorna informações sobre o timezone configurado no sistema
    """
    return {
        "system_timezone": get_brazil_timezone_info(),
        "current_time_brazil": now_brazil().isoformat(),
        "current_time_utc": now_utc().isoformat(),
        "timezone_configured": "America/Sao_Paulo"
    }

@router.get("/health")
async def health_check():
    """
    Health check do sistema
    """
    return {
        "status": "healthy",
        "service": "Sistema Vendas CEASA",
        "timestamp_brazil": now_brazil().isoformat()
    }
