import os
from typing import List

# =========================
# CONFIGURACIÓN DE ADMINISTRADORES
# =========================
ADMIN_IDS: List[int] = [7828962018]

def is_admin(user_id: int) -> bool:
    """Verifica si un usuario es administrador"""
    return user_id in ADMIN_IDS

# =========================
# CONFIGURACIÓN DE TOKENS
# =========================
BOT_TOKEN: str = "7878980636:AAFnvq7emNzPXNqj2eliCE4P7O5bhW4fZX8"

# =========================
# CONFIGURACIÓN DE BASE DE DATOS
# =========================
MONGO_URI: str = "mongodb+srv://rayomarblezh:tatico.10@telegram.yxpl0n0.mongodb.net/?retryWrites=true&w=majority&appName=Telegram&ssl=true&ssl_cert_reqs=CERT_NONE"
DB_NAME: str = "mundomi"

# =========================
# PARÁMETROS DEL SISTEMA
# =========================
MIN_DEPOSITO: float = 0.5
MIN_RETIRO: float = 1.1
COMISION_RETIRO: float = 0.1
TIEMPO_PROCESAMIENTO: str = "24-48h"

# =========================
# CONFIGURACIÓN DE LOGGING
# =========================
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

# =========================
# CONFIGURACIÓN DE API
# =========================
API_HOST: str = "0.0.0.0"
API_PORT: int = 3000
API_WORKERS: int = 1
