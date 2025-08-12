"""
Utilitários para manipulação de timezone
Centraliza as funções de conversão de data/hora para o timezone do Brasil
"""

import pytz
from datetime import datetime, date
from typing import Optional, Union
from app.core.config import settings

# Timezone do Brasil
BRAZIL_TZ = pytz.timezone(settings.TIMEZONE)
UTC_TZ = pytz.UTC


def now_brazil() -> datetime:
    """
    Retorna a data/hora atual no timezone do Brasil
    """
    return datetime.now(BRAZIL_TZ)


def now_utc() -> datetime:
    """
    Retorna a data/hora atual em UTC
    """
    return datetime.now(UTC_TZ)


def to_brazil_tz(dt: datetime) -> datetime:
    """
    Converte datetime para timezone do Brasil
    
    Args:
        dt: datetime a ser convertido
        
    Returns:
        datetime no timezone do Brasil
    """
    if dt is None:
        return None
        
    if dt.tzinfo is None:
        # Se não tem timezone, assume UTC
        dt = UTC_TZ.localize(dt)
    
    return dt.astimezone(BRAZIL_TZ)


def to_utc(dt: datetime) -> datetime:
    """
    Converte datetime para UTC
    
    Args:
        dt: datetime a ser convertido
        
    Returns:
        datetime em UTC
    """
    if dt is None:
        return None
        
    if dt.tzinfo is None:
        # Se não tem timezone, assume timezone do Brasil
        dt = BRAZIL_TZ.localize(dt)
    
    return dt.astimezone(UTC_TZ)


def localize_brazil(dt: datetime) -> datetime:
    """
    Adiciona timezone do Brasil a um datetime naive
    
    Args:
        dt: datetime sem timezone
        
    Returns:
        datetime com timezone do Brasil
    """
    if dt is None:
        return None
        
    if dt.tzinfo is not None:
        raise ValueError("Datetime já possui timezone")
    
    return BRAZIL_TZ.localize(dt)


def format_brazil_datetime(dt: Optional[datetime], format_str: str = "%d/%m/%Y %H:%M:%S") -> str:
    """
    Formata datetime no timezone do Brasil
    
    Args:
        dt: datetime a ser formatado
        format_str: formato de saída
        
    Returns:
        string formatada ou vazia se dt for None
    """
    if dt is None:
        return ""
    
    # Converte para timezone do Brasil se necessário
    dt_brazil = to_brazil_tz(dt)
    return dt_brazil.strftime(format_str)


def format_brazil_date(dt: Optional[Union[datetime, date]], format_str: str = "%d/%m/%Y") -> str:
    """
    Formata data no formato brasileiro
    
    Args:
        dt: datetime ou date a ser formatado
        format_str: formato de saída
        
    Returns:
        string formatada ou vazia se dt for None
    """
    if dt is None:
        return ""
    
    if isinstance(dt, datetime):
        # Converte para timezone do Brasil se for datetime
        dt_brazil = to_brazil_tz(dt)
        return dt_brazil.strftime(format_str)
    else:
        # Se for date, usa diretamente
        return dt.strftime(format_str)


def start_of_day_brazil(dt: Union[datetime, date]) -> datetime:
    """
    Retorna o início do dia (00:00:00) no timezone do Brasil
    
    Args:
        dt: data de referência
        
    Returns:
        datetime no início do dia no timezone do Brasil
    """
    if isinstance(dt, datetime):
        # Converte para timezone do Brasil primeiro
        dt_brazil = to_brazil_tz(dt)
        date_part = dt_brazil.date()
    else:
        date_part = dt
    
    # Cria datetime no início do dia no timezone do Brasil
    return BRAZIL_TZ.localize(datetime.combine(date_part, datetime.min.time()))


def end_of_day_brazil(dt: Union[datetime, date]) -> datetime:
    """
    Retorna o fim do dia (23:59:59.999999) no timezone do Brasil
    
    Args:
        dt: data de referência
        
    Returns:
        datetime no fim do dia no timezone do Brasil
    """
    if isinstance(dt, datetime):
        # Converte para timezone do Brasil primeiro
        dt_brazil = to_brazil_tz(dt)
        date_part = dt_brazil.date()
    else:
        date_part = dt
    
    # Cria datetime no fim do dia no timezone do Brasil
    return BRAZIL_TZ.localize(datetime.combine(date_part, datetime.max.time()))


def is_same_day_brazil(dt1: datetime, dt2: datetime) -> bool:
    """
    Verifica se dois datetimes são do mesmo dia no timezone do Brasil
    
    Args:
        dt1: primeiro datetime
        dt2: segundo datetime
        
    Returns:
        True se forem do mesmo dia no timezone do Brasil
    """
    if dt1 is None or dt2 is None:
        return False
    
    dt1_brazil = to_brazil_tz(dt1)
    dt2_brazil = to_brazil_tz(dt2)
    
    return dt1_brazil.date() == dt2_brazil.date()


def get_brazil_timezone_info() -> dict:
    """
    Retorna informações sobre o timezone do Brasil
    
    Returns:
        dict com informações do timezone
    """
    now = now_brazil()
    return {
        "timezone": str(BRAZIL_TZ),
        "current_time": now.isoformat(),
        "utc_offset": now.strftime("%z"),
        "timezone_name": now.tzname(),
        "is_dst": bool(now.dst())
    }
