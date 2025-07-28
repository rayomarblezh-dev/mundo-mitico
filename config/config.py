import os
import json
from typing import List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# =========================
# CONFIGURACIÓN DE ADMINISTRADORES
# =========================
ADMIN_IDS: List[int] = [int(x) for x in os.getenv("ADMIN_IDS").split(",")]

def is_admin(user_id: int) -> bool:
    """
    Verifica si un usuario es administrador.
    
    Args:
        user_id: ID del usuario a verificar
        
    Returns:
        True si el usuario es administrador, False en caso contrario
    """
    return user_id in ADMIN_IDS

# =========================
# CONFIGURACIÓN DE CANALES
# =========================
# IDs de canales donde el bot debe ser administrador
CHANNEL_IDS: List[str] = os.getenv("CHANNEL_IDS").split(",")

# Canales requeridos para suscripción de usuarios
REQUIRED_CHANNELS_RAW = os.getenv("REQUIRED_CHANNELS", "[]")
try:
    REQUIRED_CHANNELS: List[dict] = json.loads(REQUIRED_CHANNELS_RAW)
except (json.JSONDecodeError, TypeError):
    REQUIRED_CHANNELS: List[dict] = []

# =========================
# CONFIGURACIÓN DE TOKENS
# =========================
BOT_TOKEN: str = os.getenv("BOT_TOKEN")

# =========================
# CONFIGURACIÓN DE BASE DE DATOS
# =========================
MONGO_URI: str = os.getenv("MONGO_URI")
DB_NAME: str = os.getenv("DB_NAME")

# =========================
# PARÁMETROS DEL SISTEMA
# =========================
MIN_DEPOSITO: float = float(os.getenv("MIN_DEPOSITO"))
MIN_RETIRO: float = float(os.getenv("MIN_RETIRO"))
COMISION_RETIRO: float = float(os.getenv("COMISION_RETIRO"))
TIEMPO_PROCESAMIENTO: str = os.getenv("TIEMPO_PROCESAMIENTO")

# =========================
# CONFIGURACIÓN DE LOGGING
# =========================
LOG_LEVEL: str = os.getenv("LOG_LEVEL")
LOG_FORMAT: str = os.getenv("LOG_FORMAT")
