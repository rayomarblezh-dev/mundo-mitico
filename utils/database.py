from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Bot
import datetime

# URI de Railway MongoDB
MONGO_URI = "mongodb://mongo:PzIAIxpsrfvHQmmXESbaCkAyPPTwdWcf@tramway.proxy.rlwy.net:26295"
DB_NAME = "mundo_mitico"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Colección de usuarios y referidos
usuarios_col = db["usuarios"]
referidos_col = db["referidos"]
nfts_col = db["nfts"]

# Función de inicialización para sincronizar la base de datos
async def init_db():
    # Índice único para evitar referidos duplicados (referidor_id + referido_id)
    await referidos_col.create_index(
        [
            ("referidor_id", 1),
            ("referido_id", 1)
        ],
        unique=True,
        name="unique_referido"
    )

# Funciones base referidos
async def agregar_referido(referidor_id: int, referido_id: int):
    await referidos_col.insert_one({
        "referidor_id": referidor_id,
        "referido_id": referido_id,
        "activo": False,
        "recompensa_entregada": False
    })

async def marcar_referido_activo(referido_id: int):
    await referidos_col.update_one({"referido_id": referido_id}, {"$set": {"activo": True}})

async def obtener_referidos(referidor_id: int):
    return await referidos_col.find({"referidor_id": referidor_id}).to_list(length=100)

async def contar_referidos(referidor_id: int):
    return await referidos_col.count_documents({"referidor_id": referidor_id})

async def contar_referidos_activos(referidor_id: int):
    return await referidos_col.count_documents({"referidor_id": referidor_id, "activo": True})

# Funciones para recompensas
async def marcar_recompensa_entregada(referido_id: int):
    await referidos_col.update_one({"referido_id": referido_id}, {"$set": {"recompensa_entregada": True}})

async def recompensa_entregada(referido_id: int):
    doc = await referidos_col.find_one({"referido_id": referido_id})
    return doc and doc.get("recompensa_entregada", False)

async def notificar_recompensa(bot: Bot, user_id: int, tipo: str):
    if tipo == "hada":
        mensaje = "<b>🤩 ¡Has ganado 1 Hada por invitar a 10 amigos!</b>"
    elif tipo == "elfo":
        mensaje = "<b>🤩 ¡Has ganado 1 Elfo porque uno de tus referidos realizó su primer depósito!</b>"
    else:
        mensaje = f"<b>🤩 ¡Has ganado una recompensa de referidos!</b>"
    await bot.send_message(user_id, mensaje, parse_mode="HTML")

# Funciones para NFTs
async def usuario_tiene_nft(user_id: int):
    """Verificar si el usuario ya tiene algún NFT"""
    nft = await nfts_col.find_one({"user_id": user_id})
    return nft is not None

async def comprar_nft(user_id: int, nft_tipo: str, precio: float):
    """Registrar la compra de un NFT"""
    nft_data = {
        "user_id": user_id,
        "nft_tipo": nft_tipo,
        "precio": precio,
        "fecha_compra": datetime.datetime.now(),
        "activo": True
    }
    await nfts_col.insert_one(nft_data)

async def obtener_nft_usuario(user_id: int):
    """Obtener el NFT del usuario"""
    return await nfts_col.find_one({"user_id": user_id})