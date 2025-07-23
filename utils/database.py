from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Bot
import datetime

# URI de Railway MongoDB
MONGO_URI = "mongodb://mongo:npMengYxzYkEtSATSPFyixaPDDBmZtGE@crossover.proxy.rlwy.net:24556"
DB_NAME = "mundo_mitico_db"

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

# Solo se puede tener uno de los dos comunes (Moguri o Gárgola)
async def usuario_tiene_nft_comun(user_id: int):
    """Verificar si el usuario ya tiene un NFT común (Moguri o Gárgola)"""
    nft = await nfts_col.find_one({"user_id": user_id, "nft_tipo": {"$in": ["Moguri-NFT", "Gargola-NFT"]}})
    return nft is not None

async def usuario_tiene_nft_ghost(user_id: int):
    """Verificar si el usuario ya tiene el NFT Ghost"""
    nft = await nfts_col.find_one({"user_id": user_id, "nft_tipo": "Ghost-NFT"})
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

# =========================
# Funciones de Administración
# =========================

# Colección para usuarios y balances
usuarios_col = db["usuarios"]
creditos_col = db["creditos"]
depositos_col = db["depositos"]

async def obtener_o_crear_usuario(user_id: int, username: str = None, first_name: str = None):
    """Obtener usuario existente o crear uno nuevo"""
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        usuario_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "balance": 0.0,
            "fecha_registro": datetime.datetime.now(),
            "activo": True
        }
        await usuarios_col.insert_one(usuario_data)
        return usuario_data
    return usuario

async def obtener_balance_usuario(user_id: int) -> float:
    """Obtener el balance actual de un usuario"""
    usuario = await usuarios_col.find_one({"user_id": user_id})
    return usuario.get("balance", 0.0) if usuario else 0.0

async def agregar_credito_usuario(user_id: int, cantidad: float, razon: str, admin_id: int):
    """Agregar crédito a un usuario"""
    # Crear registro de crédito
    credito_data = {
        "user_id": user_id,
        "cantidad": cantidad,
        "razon": razon,
        "admin_id": admin_id,
        "fecha": datetime.datetime.now(),
        "tipo": "admin"
    }
    await creditos_col.insert_one(credito_data)
    
    # Actualizar balance del usuario
    await usuarios_col.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": cantidad}},
        upsert=True
    )

async def obtener_usuario_por_username(username: str):
    """Obtener usuario por username"""
    return await usuarios_col.find_one({"username": username})

async def contar_usuarios():
    """Contar total de usuarios registrados"""
    return await usuarios_col.count_documents({})

async def contar_depositos():
    """Contar total de depósitos"""
    return await depositos_col.count_documents({})

async def contar_retiros():
    """Contar total de retiros"""
    return await creditos_col.count_documents({"tipo": "retiro"})

async def obtener_depositos_pendientes():
    """Obtener depósitos pendientes de revisión"""
    return await depositos_col.find({"estado": "pendiente"}).to_list(length=50)

async def guardar_hash_pago(user_id: int, hash_text: str, network_key: str, network_name: str, address: str):
    """Guardar hash de pago en la base de datos"""
    deposito_data = {
        "user_id": user_id,
        "hash": hash_text,
        "network_key": network_key,
        "network_name": network_name,
        "address": address,
        "estado": "pendiente",
        "fecha": datetime.datetime.now()
    }
    await depositos_col.insert_one(deposito_data)

async def notificar_credito_agregado(bot, user_id: int, cantidad: float, razon: str):
    """Notificar al usuario que se le agregó crédito"""
    try:
        mensaje = (
            f"<b>💰 Crédito Agregado</b>\n\n"
            f"<i>Se ha agregado <b>{cantidad} TON</b> a tu balance.\n\n"
            f"<b>📝 Razón:</b> {razon}\n"
            f"<b>✅ Estado:</b> Crédito disponible inmediatamente</i>"
        )
        await bot.send_message(user_id, mensaje, parse_mode="HTML")
    except Exception:
        pass  # Ignorar errores de notificación

# =========================
# Paquete de bienvenida
# =========================

PAQUETE_BIENVENIDA = {
    "hada": 7,
    "mago": 3,
    "licantropo": 1
}
PAQUETE_PRECIO = 1.5

async def es_elegible_paquete_bienvenida(user_id: int):
    """Verifica si el usuario es elegible para la promo de bienvenida (menos de 15 días, no comprado ni expirado)"""
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return False
    fecha_registro = usuario.get("fecha_registro")
    if not fecha_registro:
        return False
    dias = (datetime.datetime.now() - fecha_registro).days
    paquete = usuario.get("paquete_bienvenida", {})
    if paquete.get("comprado") or paquete.get("expirado"):
        return False
    return dias < 15

async def registrar_compra_paquete_bienvenida(user_id: int):
    """Marca el paquete como comprado y agrega criaturas al inventario"""
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return False
    inventario = usuario.get("inventario", {})
    # Sumar criaturas del paquete
    for criatura, cantidad in PAQUETE_BIENVENIDA.items():
        inventario[criatura] = inventario.get(criatura, 0) + cantidad
    await usuarios_col.update_one(
        {"user_id": user_id},
        {"$set": {
            "inventario": inventario,
            "paquete_bienvenida": {"comprado": True, "expirado": False, "fecha_oferta": usuario.get("fecha_registro")}
        }}
    )
    return True

async def marcar_paquete_bienvenida_expirado(user_id: int):
    """Marca la promo como expirada"""
    await usuarios_col.update_one(
        {"user_id": user_id},
        {"$set": {"paquete_bienvenida.expirado": True}}
    )

async def usuario_compro_paquete_bienvenida(user_id: int):
    usuario = await usuarios_col.find_one({"user_id": user_id})
    paquete = usuario.get("paquete_bienvenida", {}) if usuario else {}
    return paquete.get("comprado", False)

async def usuario_paquete_bienvenida_expirado(user_id: int):
    usuario = await usuarios_col.find_one({"user_id": user_id})
    paquete = usuario.get("paquete_bienvenida", {}) if usuario else {}
    return paquete.get("expirado", False)