import os
from typing import List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv("config.env")

# =========================
# CONFIGURACIÓN DE ADMINISTRADORES
# =========================
ADMIN_IDS: List[int] = [int(x) for x in os.getenv("ADMIN_IDS", "7828962018").split(",")]

def is_admin(user_id: int) -> bool:
    """Verifica si un usuario es administrador"""
    return user_id in ADMIN_IDS

# =========================
# CONFIGURACIÓN DE CANALES
# =========================
# IDs de canales donde el bot debe ser administrador
CHANNEL_IDS: List[str] = os.getenv("CHANNEL_IDS").split(",")

# Canales requeridos para suscripción de usuarios
REQUIRED_CHANNELS: List[dict] = [
    {
        "id": "@mundomitico",
        "nombre": "Mundo Mítico", 
        "url": "https://t.me/mundomitico"
    },
    {
        "id": "@mundomiticopagos",
        "nombre": "Mundo Mítico Pagos", 
        "url": "https://t.me/mundomiticopagos"
    }
]

# =========================
# CONFIGURACIÓN DE TOKENS
# =========================
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "7878980636:AAHtshLbf-qkbwY7pVIBapuEfzcRlXaiuqo")

# =========================
# CONFIGURACIÓN DE BASE DE DATOS
# =========================
MONGO_URI: str = os.getenv("MONGO_URI", "localhost:27017")
DB_NAME: str = os.getenv("DB_NAME", "mundomi")

# =========================
# PARÁMETROS DEL SISTEMA
# =========================
MIN_DEPOSITO: float = float(os.getenv("MIN_DEPOSITO", "0.5"))
MIN_RETIRO: float = float(os.getenv("MIN_RETIRO", "1.1"))
COMISION_RETIRO: float = float(os.getenv("COMISION_RETIRO", "0.1"))
TIEMPO_PROCESAMIENTO: str = os.getenv("TIEMPO_PROCESAMIENTO", "24-48h")

# =========================
# CONFIGURACIÓN DE LOGGING
# =========================
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
