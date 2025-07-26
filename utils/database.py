from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Bot
import datetime
import logging
from config.config import MONGO_URI, DB_NAME, ADMIN_IDS
from modules.constants import SISTEMA_CONFIG

logger = logging.getLogger(__name__)

# =========================
# CONEXIÓN A BASE DE DATOS
# =========================

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# =========================
# COLECCIONES DE BASE DE DATOS
# =========================

# Colección de usuarios y referidos
usuarios_col = db["usuarios"]
referidos_col = db["referidos"]
nfts_col = db["nfts"]
creditos_col = db["creditos"]
depositos_col = db["depositos"]
admin_logs_col = db["admin_logs"]
logs_col = db["logs"]

# =========================
# CONSTANTES DEL SISTEMA
# =========================

# Usar constantes centralizadas
MIN_DEPOSITO = SISTEMA_CONFIG["min_deposito"]
MIN_RETIRO = SISTEMA_CONFIG["min_retiro"]
COMISION_RETIRO = SISTEMA_CONFIG["comision_retiro"]

# =========================
# INICIALIZACIÓN DE BASE DE DATOS
# =========================

async def init_db():
    """Inicializa la base de datos con índices y configuraciones necesarias"""
    try:
        # Índice único para evitar referidos duplicados
        await referidos_col.create_index(
            [
                ("referidor_id", 1),
                ("referido_id", 1)
            ],
            unique=True,
            name="unique_referido"
        )
        
        # Índices en user_id para búsquedas rápidas
        await usuarios_col.create_index([("user_id", 1)], unique=True, name="user_id_idx")
        await creditos_col.create_index([("user_id", 1)], name="user_id_idx_creditos")
        await depositos_col.create_index([("user_id", 1)], name="user_id_idx_depositos")
        await nfts_col.create_index([("user_id", 1)], name="user_id_idx_nfts")
        await logs_col.create_index([("actor_id", 1)], name="actor_id_idx")
        await logs_col.create_index([("timestamp", -1)], name="timestamp_idx")
        
        logger.info("✅ Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")

# =========================
# FUNCIONES DE USUARIOS
# =========================

async def obtener_o_crear_usuario(user_id: int, username: str = None, first_name: str = None):
    """Obtener usuario existente o crear uno nuevo"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            usuario_data = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "balance": 0.0,
                "inventario": {},
                "fecha_registro": datetime.datetime.now(),
                "activo": True,
                "ultima_actividad": datetime.datetime.now()
            }
            await usuarios_col.insert_one(usuario_data)
            logger.info(f"✅ Nuevo usuario creado: {user_id}")
            return usuario_data
        return usuario
    except Exception as e:
        logger.error(f"❌ Error obteniendo/creando usuario {user_id}: {e}")
        return None

async def obtener_balance_usuario(user_id: int) -> float:
    """Obtener el balance actual de un usuario"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        return usuario.get("balance", 0.0) if usuario else 0.0
    except Exception as e:
        logger.error(f"❌ Error obteniendo balance para {user_id}: {e}")
        return 0.0

async def descontar_balance_usuario(user_id: int, cantidad: float) -> bool:
    """Descontar balance de un usuario de forma atómica. Retorna True si tuvo éxito."""
    try:
        res = await usuarios_col.update_one(
            {"user_id": user_id, "balance": {"$gte": cantidad}},
            {"$inc": {"balance": -cantidad}}
        )
        return res.modified_count > 0
    except Exception as e:
        logger.error(f"❌ Error descontando balance para {user_id}: {e}")
        return False

async def agregar_balance_usuario(user_id: int, cantidad: float) -> bool:
    """Agregar balance a un usuario"""
    try:
        await usuarios_col.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": cantidad}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"❌ Error agregando balance para {user_id}: {e}")
        return False

async def obtener_inventario_usuario(user_id: int) -> dict:
    """Obtiene el inventario del usuario desde la base de datos"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            return {}
        return usuario.get("inventario", {})
    except Exception as e:
        logger.error(f"❌ Error obteniendo inventario para {user_id}: {e}")
        return {}

async def agregar_item_inventario(user_id: int, item: str, cantidad: int = 1) -> bool:
    """Agrega un item al inventario del usuario"""
    try:
        await usuarios_col.update_one(
            {"user_id": user_id},
            {"$inc": {f"inventario.{item}": cantidad}}
        )
        return True
    except Exception as e:
        logger.error(f"❌ Error agregando item {item} para {user_id}: {e}")
        return False

async def obtener_usuario_por_username(username: str):
    """Obtener usuario por username"""
    try:
        return await usuarios_col.find_one({"username": username})
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuario por username {username}: {e}")
        return None

async def actualizar_ultima_actividad(user_id: int):
    """Actualiza la última actividad del usuario"""
    try:
        await usuarios_col.update_one(
            {"user_id": user_id},
            {"$set": {"ultima_actividad": datetime.datetime.now()}}
        )
    except Exception as e:
        logger.error(f"❌ Error actualizando última actividad para {user_id}: {e}")

# =========================
# FUNCIONES DE REFERIDOS
# =========================

async def agregar_referido(referidor_id: int, referido_id: int):
    """Agregar un nuevo referido"""
    try:
        await referidos_col.insert_one({
            "referidor_id": referidor_id,
            "referido_id": referido_id,
            "activo": False,
            "recompensa_entregada": False,
            "fecha_registro": datetime.datetime.now()
        })
        logger.info(f"✅ Referido agregado: {referidor_id} -> {referido_id}")
    except Exception as e:
        logger.error(f"❌ Error agregando referido {referidor_id} -> {referido_id}: {e}")

async def marcar_referido_activo(referido_id: int):
    """Marcar un referido como activo (realizó depósito)"""
    try:
        await referidos_col.update_one(
            {"referido_id": referido_id}, 
            {"$set": {"activo": True, "fecha_activacion": datetime.datetime.now()}}
        )
        logger.info(f"✅ Referido marcado como activo: {referido_id}")
    except Exception as e:
        logger.error(f"❌ Error marcando referido activo {referido_id}: {e}")

async def obtener_referidos(referidor_id: int):
    """Obtener lista de referidos de un usuario"""
    try:
        return await referidos_col.find({"referidor_id": referidor_id}).to_list(length=100)
    except Exception as e:
        logger.error(f"❌ Error obteniendo referidos para {referidor_id}: {e}")
        return []

async def contar_referidos(referidor_id: int):
    """Contar total de referidos de un usuario"""
    try:
        return await referidos_col.count_documents({"referidor_id": referidor_id})
    except Exception as e:
        logger.error(f"❌ Error contando referidos para {referidor_id}: {e}")
        return 0

async def contar_referidos_activos(referidor_id: int):
    """Contar referidos activos de un usuario"""
    try:
        return await referidos_col.count_documents({"referidor_id": referidor_id, "activo": True})
    except Exception as e:
        logger.error(f"❌ Error contando referidos activos para {referidor_id}: {e}")
        return 0

async def marcar_recompensa_entregada(referido_id: int):
    """Marcar recompensa de referido como entregada"""
    try:
        await referidos_col.update_one(
            {"referido_id": referido_id}, 
            {"$set": {"recompensa_entregada": True}}
        )
    except Exception as e:
        logger.error(f"❌ Error marcando recompensa entregada para {referido_id}: {e}")

async def recompensa_entregada(referido_id: int):
    """Verificar si ya se entregó recompensa a un referido"""
    try:
        doc = await referidos_col.find_one({"referido_id": referido_id})
        return doc and doc.get("recompensa_entregada", False)
    except Exception as e:
        logger.error(f"❌ Error verificando recompensa para {referido_id}: {e}")
        return False

async def notificar_recompensa(bot: Bot, user_id: int, tipo: str):
    """Notificar recompensa de referidos al usuario"""
    try:
        if tipo == "hada":
            mensaje = "🤩 ¡Has ganado 1 Hada por invitar a 10 amigos!"
        elif tipo == "elfo":
            mensaje = "🤩 ¡Has ganado 1 Elfo porque uno de tus referidos realizó su primer depósito!"
        else:
            mensaje = "🤩 ¡Has ganado una recompensa de referidos!"
        
        await bot.send_message(user_id, mensaje, parse_mode="HTML")
        logger.info(f"✅ Recompensa notificada a {user_id}: {tipo}")
    except Exception as e:
        logger.error(f"❌ Error notificando recompensa a {user_id}: {e}")

async def notificar_nuevo_referido(bot: Bot, referidor_id: int, referido_id: int, referido_name: str):
    """Notificar al referidor que tiene un nuevo referido"""
    try:
        mensaje = (
            "🎉 ¡Nuevo Referido!\n\n"
            f"¡{referido_name} se ha unido usando tu enlace de referido!\n\n"
            "Recuerda las recompensas:\n"
            "• Por cada 10 referidos: 1 Hada\n"
            "• Por cada referido que invierta: 1 Elfo\n\n"
            "¡Sigue compartiendo tu enlace para obtener más recompensas!"
        )
        await bot.send_message(referidor_id, mensaje, parse_mode="HTML")
        logger.info(f"✅ Notificación de nuevo referido enviada a {referidor_id}")
    except Exception as e:
        logger.error(f"❌ Error notificando nuevo referido a {referidor_id}: {e}")

async def notificar_has_sido_referido(bot: Bot, referido_id: int, referidor_name: str):
    """Notificar al nuevo usuario que ha sido referido"""
    try:
        mensaje = (
            "👋 ¡Bienvenido a Mundo Mítico!\n\n"
            f"Has sido invitado por {referidor_name}.\n\n"
            "🎁 Beneficios por ser referido:\n"
            "• Acceso inmediato a todas las funciones\n"
            "• Soporte prioritario\n"
            "• Comunidad activa de jugadores\n\n"
            "¡Disfruta de tu aventura en el mundo mítico!"
        )
        await bot.send_message(referido_id, mensaje, parse_mode="HTML")
        logger.info(f"✅ Notificación de referido enviada a {referido_id}")
    except Exception as e:
        logger.error(f"❌ Error notificando referido a {referido_id}: {e}")

async def verificar_recompensas_referidos(bot: Bot, referidor_id: int):
    """Verificar y otorgar recompensas de referidos automáticamente"""
    try:
        # Contar referidos totales
        total_referidos = await contar_referidos(referidor_id)
        
        # Verificar recompensa por 10 referidos
        if total_referidos >= 10:
            # Verificar si ya se entregó la recompensa
            recompensa_entregada = await recompensa_entregada(referidor_id)
            if not recompensa_entregada:
                # Otorgar 1 Hada
                await agregar_item_inventario(referidor_id, "hada", 1)
                await marcar_recompensa_entregada(referidor_id)
                await notificar_recompensa(bot, referidor_id, "hada")
                logger.info(f"✅ Recompensa de 10 referidos otorgada a {referidor_id}")
        
        # Verificar referidos activos (que han hecho depósito)
        referidos_activos = await contar_referidos_activos(referidor_id)
        if referidos_activos > 0:
            # Por cada referido activo, otorgar 1 Elfo
            for _ in range(referidos_activos):
                await agregar_item_inventario(referidor_id, "elfo", 1)
                await notificar_recompensa(bot, referidor_id, "elfo")
                logger.info(f"✅ Recompensa de referido activo otorgada a {referidor_id}")
                
    except Exception as e:
        logger.error(f"❌ Error verificando recompensas de referidos para {referidor_id}: {e}")

async def procesar_nuevo_referido(bot: Bot, referidor_id: int, referido_id: int, referido_name: str, referidor_name: str):
    """Procesar completamente un nuevo referido"""
    try:
        # Agregar el referido
        await agregar_referido(referidor_id, referido_id)
        
        # Notificar al referidor
        await notificar_nuevo_referido(bot, referidor_id, referido_id, referido_name)
        
        # Notificar al referido
        await notificar_has_sido_referido(bot, referido_id, referidor_name)
        
        # Verificar recompensas del referidor
        await verificar_recompensas_referidos(bot, referidor_id)
        
        logger.info(f"✅ Nuevo referido procesado: {referidor_id} -> {referido_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error procesando nuevo referido {referidor_id} -> {referido_id}: {e}")
        return False

# =========================
# FUNCIONES DE NFTs
# =========================

async def usuario_tiene_nft_comun(user_id: int):
    """Verificar si el usuario ya tiene un NFT común (Moguri o Gárgola)"""
    try:
        nft = await nfts_col.find_one({
            "user_id": user_id, 
            "nft_tipo": {"$in": ["Moguri-NFT", "Gargola-NFT"]}
        })
        return nft is not None
    except Exception as e:
        logger.error(f"❌ Error verificando NFT común para {user_id}: {e}")
        return False

async def usuario_tiene_nft_ghost(user_id: int):
    """Verificar si el usuario ya tiene el NFT Ghost"""
    try:
        nft = await nfts_col.find_one({
            "user_id": user_id, 
            "nft_tipo": "Ghost-NFT"
        })
        return nft is not None
    except Exception as e:
        logger.error(f"❌ Error verificando NFT Ghost para {user_id}: {e}")
        return False

async def comprar_nft(user_id: int, nft_tipo: str, precio: float):
    """Registrar la compra de un NFT"""
    try:
        nft_data = {
            "user_id": user_id,
            "nft_tipo": nft_tipo,
            "precio": precio,
            "fecha_compra": datetime.datetime.now(),
            "activo": True,
            "fecha_expiracion": datetime.datetime.now() + datetime.timedelta(days=30)
        }
        await nfts_col.insert_one(nft_data)
        logger.info(f"✅ NFT comprado: {user_id} -> {nft_tipo}")
    except Exception as e:
        logger.error(f"❌ Error comprando NFT {nft_tipo} para {user_id}: {e}")

async def obtener_nft_usuario(user_id: int):
    """Obtener el NFT del usuario"""
    try:
        return await nfts_col.find_one({"user_id": user_id, "activo": True})
    except Exception as e:
        logger.error(f"❌ Error obteniendo NFT para {user_id}: {e}")
        return None

async def obtener_nfts_activos():
    """Obtener todos los NFTs activos para procesar ganancias diarias"""
    try:
        return await nfts_col.find({"activo": True}).to_list(length=1000)
    except Exception as e:
        logger.error(f"❌ Error obteniendo NFTs activos: {e}")
        return []

async def desactivar_nft_expirado(nft_id: str):
    """Desactivar un NFT que ha expirado"""
    try:
        await nfts_col.update_one(
            {"_id": nft_id},
            {"$set": {"activo": False}}
        )
        logger.info(f"✅ NFT desactivado: {nft_id}")
    except Exception as e:
        logger.error(f"❌ Error desactivando NFT {nft_id}: {e}")

# =========================
# FUNCIONES DE COMPRAS Y TRANSACCIONES
# =========================

async def procesar_compra_item(user_id: int, item: dict) -> dict:
    """
    Procesa la compra de un ítem (NFT, criatura, promo).
    item debe tener: tipo ('nft', 'criatura', 'promo'), nombre, precio
    Retorna: {'ok': True/False, 'msg': str}
    """
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            return {"ok": False, "msg": "Usuario no encontrado."}
        
        balance = usuario.get("balance", 0.0)
        if balance < item["precio"]:
            return {"ok": False, "msg": "No tienes suficiente TON para comprar este producto."}
        
        # Restricciones por tipo
        if item["tipo"] == "nft":
            if item["nombre"] in ["Moguri-NFT", "Gargola-NFT"]:
                if await usuario_tiene_nft_comun(user_id):
                    return {"ok": False, "msg": "Solo puedes tener 1 NFT común (Moguri o Gárgola) a la vez."}
            if item["nombre"] == "Ghost-NFT":
                if await usuario_tiene_nft_ghost(user_id):
                    return {"ok": False, "msg": "Solo puedes tener 1 NFT Ghost a la vez."}
            # Registrar compra NFT
            await comprar_nft(user_id, item["nombre"], item["precio"])
            
        elif item["tipo"] == "criatura":
            inventario = usuario.get("inventario", {})
            inventario[item["nombre"]] = inventario.get(item["nombre"], 0) + 1
            await usuarios_col.update_one(
                {"user_id": user_id},
                {"$set": {"inventario": inventario}}
            )
            
        elif item["tipo"] == "promo":
            ok = await registrar_compra_paquete_bienvenida(user_id)
            if not ok:
                return {"ok": False, "msg": "No se pudo procesar la promoción."}
        
        # Descontar TON de forma atómica
        ok = await descontar_balance_usuario(user_id, item["precio"])
        if not ok:
            return {"ok": False, "msg": "No tienes suficiente TON para comprar este producto."}
        
        await log_action(user_id, "compra_realizada", details={
            "tipo": item["tipo"], 
            "nombre": item["nombre"], 
            "precio": item["precio"]
        })
        
        logger.info(f"✅ Compra exitosa: {user_id} -> {item['nombre']}")
        return {"ok": True, "msg": "¡Compra exitosa!"}
        
    except Exception as e:
        logger.error(f"❌ Error procesando compra para {user_id}: {e}")
        return {"ok": False, "msg": "Error interno del sistema."}

# =========================
# FUNCIONES DE DEPÓSITOS Y RETIROS
# =========================

async def guardar_hash_pago(user_id: int, hash_text: str, network_key: str, network_name: str, address: str, cantidad: float = None):
    """Guardar hash de pago en la base de datos"""
    try:
        deposito_data = {
            "user_id": user_id,
            "hash": hash_text,
            "network_key": network_key,
            "network_name": network_name,
            "address": address,
            "cantidad": cantidad,
            "estado": "pendiente",
            "fecha": datetime.datetime.now()
        }
        result = await depositos_col.insert_one(deposito_data)
        logger.info(f"✅ Hash de pago guardado: {user_id} -> {hash_text}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"❌ Error guardando hash de pago para {user_id}: {e}")
        return None

async def procesar_deposito(deposito_id: str, admin_id: int, cantidad_real: float):
    """Procesar un depósito pendiente"""
    try:
        deposito = await depositos_col.find_one({"_id": deposito_id})
        if not deposito:
            return False
        
        user_id = deposito["user_id"]
        
        # Actualizar estado del depósito
        await depositos_col.update_one(
            {"_id": deposito_id},
            {
                "$set": {
                    "estado": "procesado",
                    "cantidad_real": cantidad_real,
                    "admin_id": admin_id,
                    "fecha_procesamiento": datetime.datetime.now()
                }
            }
        )
        
        # Agregar balance al usuario
        await agregar_balance_usuario(user_id, cantidad_real)
        
        # Marcar referido como activo si es su primer depósito
        await marcar_referido_activo(user_id)
        
        # Verificar recompensas de referidos para el referidor
        try:
            from modules.bot import bot
            await verificar_recompensas_referidos(bot, user_id)
        except Exception as e:
            logger.error(f"Error verificando recompensas de referidos para {user_id}: {e}")
        
        await log_action(admin_id, "deposito_procesado", target_id=user_id, details={
            "deposito_id": deposito_id,
            "cantidad": cantidad_real
        })
        
        logger.info(f"✅ Depósito procesado: {deposito_id} -> {cantidad_real} TON")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando depósito {deposito_id}: {e}")
        return False

async def solicitar_retiro(user_id: int, cantidad: float, wallet_address: str):
    """Solicitar un retiro"""
    try:
        # Verificar balance
        balance = await obtener_balance_usuario(user_id)
        if balance < cantidad:
            return {"ok": False, "msg": "Balance insuficiente"}
        
        if cantidad < MIN_RETIRO:
            return {"ok": False, "msg": f"El monto mínimo de retiro es {MIN_RETIRO} TON"}
        
        # Calcular comisión
        comision = cantidad * COMISION_RETIRO
        cantidad_final = cantidad - comision
        
        retiro_data = {
            "user_id": user_id,
            "cantidad_solicitada": cantidad,
            "comision": comision,
            "cantidad_final": cantidad_final,
            "wallet_address": wallet_address,
            "estado": "pendiente",
            "fecha_solicitud": datetime.datetime.now()
        }
        
        result = await creditos_col.insert_one(retiro_data)
        retiro_id = str(result.inserted_id)
        
        # Descontar balance
        await descontar_balance_usuario(user_id, cantidad)
        
        await log_action(user_id, "retiro_solicitado", details={
            "cantidad": cantidad,
            "wallet": wallet_address,
            "retiro_id": retiro_id
        })
        
        logger.info(f"✅ Retiro solicitado: {user_id} -> {cantidad} TON")
        return {"ok": True, "retiro_id": retiro_id}
        
    except Exception as e:
        logger.error(f"❌ Error solicitando retiro para {user_id}: {e}")
        return {"ok": False, "msg": "Error interno del sistema"}

async def procesar_retiro(retiro_id: str, admin_id: int):
    """Procesar un retiro pendiente"""
    try:
        retiro = await creditos_col.find_one({"_id": retiro_id})
        if not retiro:
            return False
        
        # Actualizar estado del retiro
        await creditos_col.update_one(
            {"_id": retiro_id},
            {
                "$set": {
                    "estado": "procesado",
                    "admin_id": admin_id,
                    "fecha_procesamiento": datetime.datetime.now()
                }
            }
        )
        
        await log_action(admin_id, "retiro_procesado", target_id=retiro["user_id"], details={
            "retiro_id": retiro_id,
            "cantidad": retiro["cantidad_final"]
        })
        
        logger.info(f"✅ Retiro procesado: {retiro_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando retiro {retiro_id}: {e}")
        return False

# =========================
# FUNCIONES DE PAQUETE DE BIENVENIDA
# =========================

PAQUETE_BIENVENIDA = {
    "hada": 7,
    "mago": 3,
    "licantropo": 1
}
PAQUETE_PRECIO = 1.5

async def es_elegible_paquete_bienvenida(user_id: int):
    """Verifica si el usuario es elegible para la promo de bienvenida"""
    try:
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
    except Exception as e:
        logger.error(f"❌ Error verificando elegibilidad paquete bienvenida para {user_id}: {e}")
        return False

async def registrar_compra_paquete_bienvenida(user_id: int):
    """Marca el paquete como comprado y agrega criaturas al inventario"""
    try:
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
                "paquete_bienvenida": {
                    "comprado": True, 
                    "expirado": False, 
                    "fecha_oferta": usuario.get("fecha_registro")
                }
            }}
        )
        
        logger.info(f"✅ Paquete bienvenida comprado: {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error registrando paquete bienvenida para {user_id}: {e}")
        return False

async def marcar_paquete_bienvenida_expirado(user_id: int):
    """Marca la promo como expirada"""
    try:
        await usuarios_col.update_one(
            {"user_id": user_id},
            {"$set": {"paquete_bienvenida.expirado": True}}
        )
    except Exception as e:
        logger.error(f"❌ Error marcando paquete expirado para {user_id}: {e}")

async def usuario_compro_paquete_bienvenida(user_id: int):
    """Verificar si el usuario ya compró el paquete de bienvenida"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        paquete = usuario.get("paquete_bienvenida", {}) if usuario else {}
        return paquete.get("comprado", False)
    except Exception as e:
        logger.error(f"❌ Error verificando compra paquete bienvenida para {user_id}: {e}")
        return False

async def usuario_paquete_bienvenida_expirado(user_id: int):
    """Verificar si el paquete de bienvenida expiró"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        paquete = usuario.get("paquete_bienvenida", {}) if usuario else {}
        return paquete.get("expirado", False)
    except Exception as e:
        logger.error(f"❌ Error verificando expiración paquete bienvenida para {user_id}: {e}")
        return False

# =========================
# FUNCIONES DE ADMINISTRACIÓN
# =========================

async def agregar_credito_usuario(user_id: int, cantidad: float, admin_id: int):
    """Agregar crédito a un usuario (función de administración)"""
    try:
        # Crear registro de crédito
        credito_data = {
            "user_id": user_id,
            "cantidad": cantidad,
            "admin_id": admin_id,
            "fecha": datetime.datetime.now(),
            "tipo": "admin"
        }
        await creditos_col.insert_one(credito_data)
        
        # Actualizar balance del usuario
        await agregar_balance_usuario(user_id, cantidad)
        
        # Log de auditoría
        await log_admin_action(admin_id, "agregar_credito", target_id=user_id, extra={"cantidad": cantidad})
        
        logger.info(f"✅ Crédito agregado por admin: {admin_id} -> {user_id}: {cantidad} TON")
        return True
    except Exception as e:
        logger.error(f"❌ Error agregando crédito: {e}")
        return False

async def log_admin_action(admin_id: int, action: str, target_id: int = None, extra: dict = None):
    """Registrar acción de administrador"""
    try:
        log = {
            "admin_id": admin_id,
            "action": action,
            "target_id": target_id,
            "extra": extra or {},
            "fecha": datetime.datetime.now()
        }
        await admin_logs_col.insert_one(log)
    except Exception as e:
        logger.error(f"❌ Error registrando acción de admin: {e}")

async def contar_usuarios():
    """Contar total de usuarios registrados"""
    try:
        return await usuarios_col.count_documents({})
    except Exception as e:
        logger.error(f"❌ Error contando usuarios: {e}")
        return 0

async def contar_depositos():
    """Contar total de depósitos"""
    try:
        return await depositos_col.count_documents({})
    except Exception as e:
        logger.error(f"❌ Error contando depósitos: {e}")
        return 0

async def contar_retiros():
    """Contar total de retiros"""
    try:
        return await creditos_col.count_documents({"tipo": "retiro"})
    except Exception as e:
        logger.error(f"❌ Error contando retiros: {e}")
        return 0

async def obtener_depositos_pendientes():
    """Obtener depósitos pendientes de revisión"""
    try:
        return await depositos_col.find({"estado": "pendiente"}).to_list(length=50)
    except Exception as e:
        logger.error(f"❌ Error obteniendo depósitos pendientes: {e}")
        return []

async def obtener_retiros_pendientes():
    """Obtener retiros pendientes de procesamiento"""
    try:
        return await creditos_col.find({"estado": "pendiente"}).to_list(length=50)
    except Exception as e:
        logger.error(f"❌ Error obteniendo retiros pendientes: {e}")
        return []

# =========================
# FUNCIONES DE NOTIFICACIONES
# =========================

async def notificar_credito_agregado(bot, user_id: int, cantidad: float, razon: str):
    """Notificar al usuario que se le agregó crédito"""
    try:
        mensaje = (
            f"💰 Crédito Agregado\n\n"
            f"Se ha agregado {cantidad} TON a tu balance.\n\n"
            f"Razón: {razon}\n"
            f"Estado: Crédito disponible inmediatamente"
        )
        await bot.send_message(user_id, mensaje, parse_mode="HTML")
        logger.info(f"✅ Notificación de crédito enviada a {user_id}")
    except Exception as e:
        logger.error(f"❌ Error notificando crédito a {user_id}: {e}")

async def notificar_admins_nuevo_deposito(user_id, cantidad, red, deposito_id):
    """Notificar a administradores sobre nuevo depósito"""
    try:
        from modules.bot import bot
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"🔔 Nuevo depósito pendiente\n\n"
                    f"ID: {deposito_id}\n"
                    f"Usuario: {user_id}\n"
                    f"Cantidad: {cantidad} {red}\n"
                    f"Revisa el panel de administración para gestionarlo.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        logger.info(f"✅ Admins notificados sobre depósito: {deposito_id}")
    except Exception as e:
        logger.error(f"❌ Error notificando admins sobre depósito: {e}")

async def notificar_admins_nuevo_retiro(user_id, cantidad, wallet, retiro_id):
    """Notificar a administradores sobre nuevo retiro"""
    try:
        from modules.bot import bot
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"🔔 Nuevo retiro pendiente\n\n"
                    f"ID: {retiro_id}\n"
                    f"Usuario: {user_id}\n"
                    f"Cantidad: {cantidad} TON\n"
                    f"Wallet: {wallet}\n"
                    f"Revisa el panel de administración para gestionarlo.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        logger.info(f"✅ Admins notificados sobre retiro: {retiro_id}")
    except Exception as e:
        logger.error(f"❌ Error notificando admins sobre retiro: {e}")

# =========================
# FUNCIONES DE LOGGING Y AUDITORÍA
# =========================

async def log_action(actor_id: int, action: str, target_id: int = None, details: dict = None):
    """Registrar acción en el sistema de logs"""
    try:
        log = {
            "actor_id": actor_id,
            "action": action,
            "target_id": target_id,
            "details": details or {},
            "timestamp": datetime.datetime.now()
        }
        await logs_col.insert_one(log)
    except Exception as e:
        logger.error(f"❌ Error registrando log: {e}")

# =========================
# FUNCIONES DE PROMOCIONES Y TIEMPO
# =========================

async def get_last_promo_time(user_id: int):
    """Obtener última vez que se mostró promoción al usuario"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if usuario:
            return usuario.get("last_promo_time")
        return None
    except Exception as e:
        logger.error(f"❌ Error obteniendo última promoción para {user_id}: {e}")
        return None

async def set_last_promo_time(user_id: int, dt: datetime.datetime):
    """Establecer última vez que se mostró promoción al usuario"""
    try:
        await usuarios_col.update_one(
            {"user_id": user_id}, 
            {"$set": {"last_promo_time": dt}}
        )
    except Exception as e:
        logger.error(f"❌ Error estableciendo última promoción para {user_id}: {e}")

# =========================
# FUNCIONES DE ESTADÍSTICAS Y REPORTES
# =========================

async def obtener_estadisticas_generales():
    """Obtener estadísticas generales del sistema"""
    try:
        total_usuarios = await contar_usuarios()
        total_depositos = await contar_depositos()
        total_retiros = await contar_retiros()
        
        # Calcular volumen total
        pipeline = [
            {"$match": {"estado": "procesado"}},
            {"$group": {"_id": None, "total": {"$sum": "$cantidad_real"}}}
        ]
        depositos_procesados = await depositos_col.aggregate(pipeline).to_list(length=1)
        volumen_total = depositos_procesados[0]["total"] if depositos_procesados else 0
        
        return {
            "total_usuarios": total_usuarios,
            "total_depositos": total_depositos,
            "total_retiros": total_retiros,
            "volumen_total": volumen_total
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return {}

async def obtener_usuarios_activos(dias: int = 7):
    """Obtener usuarios activos en los últimos N días"""
    try:
        fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
        return await usuarios_col.count_documents({
            "ultima_actividad": {"$gte": fecha_limite}
        })
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuarios activos: {e}")
        return 0

# =========================
# FUNCIONES DE LIMPIEZA Y MANTENIMIENTO
# =========================

async def limpiar_logs_antiguos(dias: int = 30):
    """Limpiar logs antiguos para mantener la base de datos optimizada"""
    try:
        fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
        result = await logs_col.delete_many({"timestamp": {"$lt": fecha_limite}})
        logger.info(f"✅ Logs antiguos limpiados: {result.deleted_count} registros")
        return result.deleted_count
    except Exception as e:
        logger.error(f"❌ Error limpiando logs antiguos: {e}")
        return 0

async def verificar_nfts_expirados():
    """Verificar y desactivar NFTs expirados"""
    try:
        fecha_actual = datetime.datetime.now()
        nfts_expirados = await nfts_col.find({
            "activo": True,
            "fecha_expiracion": {"$lt": fecha_actual}
        }).to_list(length=1000)
        
        for nft in nfts_expirados:
            await desactivar_nft_expirado(str(nft["_id"]))
        
        logger.info(f"✅ NFTs expirados verificados: {len(nfts_expirados)} desactivados")
        return len(nfts_expirados)
    except Exception as e:
        logger.error(f"❌ Error verificando NFTs expirados: {e}")
        return 0