from motor.motor_asyncio import AsyncIOMotorClient

# URI de Railway MongoDB
MONGO_URI = "mongodb://mongo:PzIAIxpsrfvHQmmXESbaCkAyPPTwdWcf@tramway.proxy.rlwy.net:26295"
DB_NAME = "mundo_mitico"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Colección de usuarios y referidos
usuarios_col = db["usuarios"]
referidos_col = db["referidos"]

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