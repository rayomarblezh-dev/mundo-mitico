import os

# --- Seguridad y administración ---
ADMIN_IDS = [
    int(x) for x in "7828962018".split(",")
]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# --- Tokens y claves ---
BOT_TOKEN = "7878980636:AAFnvq7emNzPXNqj2eliCE4P7O5bhW4fZX8"

# --- Base de datos ---
MONGO_URI = "mongodb://mongo:npMengYxzYkEtSATSPFyixaPDDBmZtGE@crossover.proxy.rlwy.net:24556"
DB_NAME = "mundo_mitico"

# --- Parámetros del sistema ---
MIN_DEPOSITO = 0.5
MIN_RETIRO = 1.1
COMISION_RETIRO = 0.1
TIEMPO_PROCESAMIENTO = "24-48h"
