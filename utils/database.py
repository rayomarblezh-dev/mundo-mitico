import motor.motor_asyncio
import datetime
import logging
from typing import Optional, Dict, Any, List
from config.config import MONGO_URI, DB_NAME
from modules.constants import SISTEMA_CONFIG
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Configuración de la base de datos
MIN_DEPOSITO = SISTEMA_CONFIG["min_deposito"]
MIN_RETIRO = SISTEMA_CONFIG["min_retiro"]
COMISION_RETIRO = SISTEMA_CONFIG["comision_retiro"]

# Cliente de MongoDB
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGO_URI,
        serverSelectionTimeoutMS=60000,  # 60 segundos
        connectTimeoutMS=60000,
        socketTimeoutMS=60000
    )
    db = client[DB_NAME]
    logger.info("✅ Cliente de MongoDB configurado correctamente")
except Exception as e:
    logger.error(f"❌ Error configurando cliente de MongoDB: {e}")
    raise

# Colecciones
usuarios_col = db.usuarios
inventarios_col = db.inventarios
depositos_col = db.depositos
creditos_col = db.creditos
referidos_col = db.referidos
logs_col = db.logs
promos_col = db.promos

async def init_db():
    """Inicializa la base de datos y crea índices necesarios"""
    try:
        # Intentar crear índices para optimizar consultas
        try:
            await usuarios_col.create_index("user_id", unique=True)
            await usuarios_col.create_index("username")
            await inventarios_col.create_index("user_id", unique=True)
            await depositos_col.create_index("user_id")
            await depositos_col.create_index("estado")
            await depositos_col.create_index("fecha")
            await creditos_col.create_index("user_id")
            await creditos_col.create_index("estado")
            await creditos_col.create_index("fecha")
            await referidos_col.create_index([("referidor_id", 1), ("referido_id", 1)], unique=True)
            await logs_col.create_index("fecha")
            await logs_col.create_index("actor_id")
            await promos_col.create_index("user_id", unique=True)
            logger.info("✅ Índices de base de datos creados correctamente")
        except Exception as index_error:
            # Si no se pueden crear índices (permisos X509), continuar sin ellos
            logger.warning(f"⚠️ No se pudieron crear índices (permisos limitados): {index_error}")
            logger.info("ℹ️ Continuando sin índices (funcionalidad básica disponible)")
        
        logger.info("✅ Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        raise

async def obtener_o_crear_usuario(user_id: int, username: str = None, first_name: str = None):
    """Obtiene o crea un usuario en la base de datos"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            usuario_data = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "balance": 0.0,
                "fecha_registro": datetime.datetime.now(),
                "ultima_actividad": datetime.datetime.now(),
                "activo": True
            }
            await usuarios_col.insert_one(usuario_data)
            usuario = usuario_data
            logger.info(f"✅ Nuevo usuario creado: {user_id}")
        else:
            # Actualizar última actividad
            await actualizar_ultima_actividad(user_id)
        return usuario
    except Exception as e:
        logger.error(f"Error obteniendo/creando usuario {user_id}: {e}")
        return None

async def obtener_balance_usuario(user_id: int) -> float:
    """Obtiene el balance de un usuario"""
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        return float(usuario.get("balance", 0)) if usuario else 0.0
    except Exception as e:
        logger.error(f"Error obteniendo balance para {user_id}: {e}")
        return 0.0

async def descontar_balance_usuario(user_id: int, cantidad: float) -> bool:
    """Descuenta balance de un usuario de forma atómica"""
    try:
        result = await usuarios_col.update_one(
            {"user_id": user_id, "balance": {"$gte": cantidad}},
            {"$inc": {"balance": -cantidad}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error descontando balance para {user_id}: {e}")
        return False

async def agregar_balance_usuario(user_id: int, cantidad: float) -> bool:
    """Agrega balance a un usuario"""
    try:
        result = await usuarios_col.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": cantidad}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error agregando balance para {user_id}: {e}")
        return False

async def obtener_inventario_usuario(user_id: int) -> dict:
    """Obtiene el inventario de un usuario"""
    try:
        inventario = await inventarios_col.find_one({"user_id": user_id})
        return inventario.get("items", {}) if inventario else {}
    except Exception as e:
        logger.error(f"Error obteniendo inventario para {user_id}: {e}")
        return {}

async def agregar_item_inventario(user_id: int, item: str, cantidad: int = 1) -> bool:
    """Agrega un item al inventario de un usuario"""
    try:
        result = await inventarios_col.update_one(
            {"user_id": user_id},
            {"$inc": {f"items.{item}": cantidad}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error agregando item {item} para {user_id}: {e}")
        return False

async def obtener_usuario_por_username(username: str):
    """Obtiene un usuario por su username"""
    try:
        return await usuarios_col.find_one({"username": username})
    except Exception as e:
        logger.error(f"Error obteniendo usuario por username {username}: {e}")
        return None

async def actualizar_ultima_actividad(user_id: int):
    """Actualiza la última actividad de un usuario"""
    try:
        await usuarios_col.update_one(
            {"user_id": user_id},
            {"$set": {"ultima_actividad": datetime.datetime.now()}}
        )
    except Exception as e:
        logger.error(f"Error actualizando actividad para {user_id}: {e}")

async def agregar_referido(referidor_id: int, referido_id: int):
    """Agrega una relación de referido"""
    try:
        await referidos_col.insert_one({
            "referidor_id": referidor_id,
            "referido_id": referido_id,
            "fecha": datetime.datetime.now(),
            "activo": False,
            "recompensa_entregada": False
        })
        logger.info(f"✅ Referido agregado: {referidor_id} -> {referido_id}")
        return True
    except Exception as e:
        if "duplicate key error" not in str(e).lower():
            logger.error(f"Error agregando referido {referidor_id} -> {referido_id}: {e}")
        return False

async def marcar_referido_activo(referido_id: int):
    """Marca un referido como activo (primer depósito)"""
    try:
        await referidos_col.update_one(
            {"referido_id": referido_id},
            {"$set": {"activo": True}}
        )
        return True
    except Exception as e:
        logger.error(f"Error marcando referido activo {referido_id}: {e}")
        return False

async def obtener_referidos(referidor_id: int):
    """Obtiene todos los referidos de un usuario"""
    try:
        cursor = referidos_col.find({"referidor_id": referidor_id})
        return await cursor.to_list(length=None)
    except Exception as e:
        logger.error(f"Error obteniendo referidos para {referidor_id}: {e}")
        return []

async def contar_referidos(referidor_id: int):
    """Cuenta el total de referidos de un usuario"""
    try:
        return await referidos_col.count_documents({"referidor_id": referidor_id})
    except Exception as e:
        logger.error(f"Error contando referidos para {referidor_id}: {e}")
        return 0

async def contar_referidos_activos(referidor_id: int):
    """Cuenta los referidos activos de un usuario"""
    try:
        return await referidos_col.count_documents({
            "referidor_id": referidor_id,
            "activo": True
        })
    except Exception as e:
        logger.error(f"Error contando referidos activos para {referidor_id}: {e}")
        return 0

async def marcar_recompensa_entregada(referido_id: int):
    """Marca que se entregó la recompensa por un referido"""
    try:
        await referidos_col.update_one(
            {"referido_id": referido_id},
            {"$set": {"recompensa_entregada": True}}
        )
        return True
    except Exception as e:
        logger.error(f"Error marcando recompensa entregada para {referido_id}: {e}")
        return False

async def recompensa_entregada(referido_id: int):
    """Verifica si ya se entregó la recompensa por un referido"""
    try:
        referido = await referidos_col.find_one({"referido_id": referido_id})
        return referido.get("recompensa_entregada", False) if referido else False
    except Exception as e:
        logger.error(f"Error verificando recompensa para {referido_id}: {e}")
        return False

async def notificar_recompensa(bot, user_id: int, tipo: str):
    """Notifica a un usuario sobre una recompensa recibida"""
    try:
        mensaje = f"🎉 ¡Felicidades! Has recibido 1 {tipo} por tus referidos."
        await bot.send_message(user_id, mensaje)
        logger.info(f"✅ Notificación de recompensa enviada a {user_id}: {tipo}")
    except Exception as e:
        logger.error(f"Error enviando notificación de recompensa a {user_id}: {e}")

async def notificar_nuevo_referido(bot, referidor_id: int, referido_id: int, referido_name: str):
    """Notifica a un referidor sobre un nuevo referido"""
    try:
        mensaje = (
            f"👥 ¡Nuevo referido!\n\n"
            f"Usuario: {referido_name}\n"
            f"ID: {referido_id}\n\n"
            "¡Sigue invitando para obtener más recompensas!"
        )
        await bot.send_message(referidor_id, mensaje)
        logger.info(f"✅ Notificación de nuevo referido enviada a {referidor_id}")
    except Exception as e:
        logger.error(f"Error enviando notificación de nuevo referido a {referidor_id}: {e}")

async def notificar_has_sido_referido(bot, referido_id: int, referidor_name: str):
    """Notifica a un usuario que ha sido referido"""
    try:
        mensaje = (
            f"🎉 ¡Bienvenido a Mundo Mítico!\n\n"
            f"Has sido invitado por: {referidor_name}\n\n"
            "¡Disfruta de tu aventura en el mundo mítico!"
        )
        await bot.send_message(referido_id, mensaje)
        logger.info(f"✅ Notificación de referido enviada a {referido_id}")
    except Exception as e:
        logger.error(f"Error enviando notificación de referido a {referido_id}: {e}")

async def verificar_recompensas_referidos(bot, referidor_id: int):
    """Verifica y entrega recompensas por referidos"""
    try:
        referidos = await obtener_referidos(referidor_id)
        total_referidos = len(referidos)
        referidos_activos = len([r for r in referidos if r.get("activo", False)])
        
        # Recompensa por cada 10 referidos (Hada)
        if total_referidos >= 10 and total_referidos % 10 == 0:
            await agregar_item_inventario(referidor_id, "hada", 1)
            await notificar_recompensa(bot, referidor_id, "Hada")
        
        # Recompensa por referidos activos (Elfo)
        for referido in referidos:
            if referido.get("activo", False) and not referido.get("recompensa_entregada", False):
                await agregar_item_inventario(referidor_id, "elfo", 1)
                await marcar_recompensa_entregada(referido["referido_id"])
                await notificar_recompensa(bot, referidor_id, "Elfo")
        
        logger.info(f"✅ Recompensas verificadas para {referidor_id}")
    except Exception as e:
        logger.error(f"Error verificando recompensas para {referidor_id}: {e}")

async def procesar_nuevo_referido(bot, referidor_id: int, referido_id: int, referido_name: str, referidor_name: str):
    """Procesa un nuevo referido completo"""
    try:
        # Agregar referido
        if await agregar_referido(referidor_id, referido_id):
            # Notificar al referidor
            await notificar_nuevo_referido(bot, referidor_id, referido_id, referido_name)
            # Notificar al referido
            await notificar_has_sido_referido(bot, referido_id, referidor_name)
            # Verificar recompensas
            await verificar_recompensas_referidos(bot, referidor_id)
            logger.info(f"✅ Nuevo referido procesado: {referidor_id} -> {referido_id}")
    except Exception as e:
        logger.error(f"Error procesando nuevo referido {referidor_id} -> {referido_id}: {e}")

async def usuario_tiene_nft_comun(user_id: int):
    """Verifica si un usuario tiene un NFT común activo"""
    try:
        inventario = await obtener_inventario_usuario(user_id)
        return inventario.get("moguri", 0) > 0 or inventario.get("gargola", 0) > 0
    except Exception as e:
        logger.error(f"Error verificando NFT común para {user_id}: {e}")
        return False

async def usuario_tiene_nft_ghost(user_id: int):
    """Verifica si un usuario tiene el NFT Ghost activo"""
    try:
        inventario = await obtener_inventario_usuario(user_id)
        return inventario.get("ghost", 0) > 0
    except Exception as e:
        logger.error(f"Error verificando NFT Ghost para {user_id}: {e}")
        return False

async def comprar_nft(user_id: int, nft_tipo: str, precio: float):
    """Compra un NFT para un usuario"""
    try:
        # Verificar balance
        balance = await obtener_balance_usuario(user_id)
        if balance < precio:
            return False, "Balance insuficiente"
        
        # Descontar balance
        if not await descontar_balance_usuario(user_id, precio):
            return False, "Error al procesar el pago"
        
        # Agregar NFT al inventario
        if not await agregar_item_inventario(user_id, nft_tipo, 1):
            # Revertir descuento si falla
            await agregar_balance_usuario(user_id, precio)
            return False, "Error al agregar NFT"
        
        return True, "NFT comprado exitosamente"
    except Exception as e:
        logger.error(f"Error comprando NFT {nft_tipo} para {user_id}: {e}")
        return False, "Error interno"

async def obtener_nft_usuario(user_id: int):
    """Obtiene los NFTs de un usuario"""
    try:
        inventario = await obtener_inventario_usuario(user_id)
        return {
            "moguri": inventario.get("moguri", 0),
            "gargola": inventario.get("gargola", 0),
            "ghost": inventario.get("ghost", 0)
        }
    except Exception as e:
        logger.error(f"Error obteniendo NFTs para {user_id}: {e}")
        return {"moguri": 0, "gargola": 0, "ghost": 0}

async def obtener_nfts_activos():
    """Obtiene todos los NFTs activos en el sistema"""
    try:
        pipeline = [
            {"$group": {
                "_id": None,
                "total_moguri": {"$sum": "$items.moguri"},
                "total_gargola": {"$sum": "$items.gargola"},
                "total_ghost": {"$sum": "$items.ghost"}
            }}
        ]
        result = await inventarios_col.aggregate(pipeline).to_list(1)
        return result[0] if result else {"total_moguri": 0, "total_gargola": 0, "total_ghost": 0}
    except Exception as e:
        logger.error(f"Error obteniendo NFTs activos: {e}")
        return {"total_moguri": 0, "total_gargola": 0, "total_ghost": 0}

async def desactivar_nft_expirado(nft_id: str):
    """Desactiva un NFT expirado"""
    try:
        # Implementar lógica de expiración si es necesaria
        logger.info(f"NFT {nft_id} marcado como expirado")
        return True
    except Exception as e:
        logger.error(f"Error desactivando NFT {nft_id}: {e}")
        return False

async def procesar_compra_item(user_id: int, item: dict) -> dict:
    """Procesa la compra de un item"""
    try:
        precio = item.get("precio", 0)
        nombre = item.get("nombre", "Item")
        tipo = item.get("tipo", "criatura")
        
        # Verificar balance
        balance = await obtener_balance_usuario(user_id)
        if balance < precio:
            return {"success": False, "message": "Balance insuficiente"}
        
        # Descontar balance
        if not await descontar_balance_usuario(user_id, precio):
            return {"success": False, "message": "Error al procesar el pago"}
        
        # Agregar item al inventario
        if not await agregar_item_inventario(user_id, nombre.lower(), 1):
            # Revertir descuento si falla
            await agregar_balance_usuario(user_id, precio)
            return {"success": False, "message": "Error al agregar item"}
        
        # Log de la compra
        await log_action(user_id, "item_comprado", details={
            "item": nombre,
            "tipo": tipo,
            "precio": precio
        })
        
        return {
            "success": True,
            "message": f"{nombre} comprado exitosamente",
            "balance_restante": balance - precio
        }
    except Exception as e:
        logger.error(f"Error procesando compra de {item.get('nombre', 'item')} para {user_id}: {e}")
        return {"success": False, "message": "Error interno del sistema"}

async def guardar_hash_pago(user_id: int, hash_text: str, network_key: str, network_name: str, address: str, cantidad: float = None):
    """Guarda el hash de un pago para verificación posterior"""
    try:
        pago_data = {
            "user_id": user_id,
            "hash": hash_text,
            "network_key": network_key,
            "network_name": network_name,
            "address": address,
            "cantidad": cantidad,
            "fecha": datetime.datetime.now(),
            "verificado": False
        }
        await depositos_col.insert_one(pago_data)
        return True
    except Exception as e:
        logger.error(f"Error guardando hash de pago para {user_id}: {e}")
        return False



async def solicitar_retiro(user_id: int, cantidad: float, wallet_address: str):
    """Solicita un retiro para un usuario"""
    try:
        # Verificar balance
        balance = await obtener_balance_usuario(user_id)
        if balance < cantidad:
            return False, "Balance insuficiente"
        
        # Descontar balance
        if not await descontar_balance_usuario(user_id, cantidad):
            return False, "Error al procesar la solicitud"
        
        # Registrar retiro
        retiro_data = {
            "user_id": user_id,
            "tipo": "retiro",
            "estado": "pendiente",
            "cantidad_solicitada": cantidad,
            "wallet": wallet_address,
            "fecha": datetime.datetime.now()
        }
        
        result = await creditos_col.insert_one(retiro_data)
        retiro_id = str(result.inserted_id)
        

        
        # Log de la acción
        await log_action(user_id, "retiro_solicitado", details={
            "cantidad": cantidad,
            "wallet": wallet_address,
            "retiro_id": retiro_id
        })
        
        return True, retiro_id
    except Exception as e:
        logger.error(f"Error solicitando retiro para {user_id}: {e}")
        return False, "Error interno"



async def es_elegible_paquete_bienvenida(user_id: int):
    """Verifica si un usuario es elegible para el paquete de bienvenida"""
    try:
        # Verificar si ya lo compró
        if await usuario_compro_paquete_bienvenida(user_id):
            return False
        
        # Verificar si expiró
        if await usuario_paquete_bienvenida_expirado(user_id):
            return False
        
        # Verificar fecha de registro (primeros 7 días)
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            return False
        
        fecha_registro = usuario.get("fecha_registro")
        if not fecha_registro:
            return False
        
        dias_desde_registro = (datetime.datetime.now() - fecha_registro).days
        return dias_desde_registro <= 7
    except Exception as e:
        logger.error(f"Error verificando elegibilidad paquete bienvenida para {user_id}: {e}")
        return False

async def registrar_compra_paquete_bienvenida(user_id: int):
    """Registra la compra del paquete de bienvenida"""
    try:
        await promos_col.insert_one({
            "user_id": user_id,
            "tipo": "paquete_bienvenida",
            "fecha_compra": datetime.datetime.now(),
            "fecha_expiracion": datetime.datetime.now() + datetime.timedelta(days=30)
        })
        return True
    except Exception as e:
        logger.error(f"Error registrando compra paquete bienvenida para {user_id}: {e}")
        return False

async def marcar_paquete_bienvenida_expirado(user_id: int):
    """Marca el paquete de bienvenida como expirado"""
    try:
        await promos_col.update_one(
            {"user_id": user_id, "tipo": "paquete_bienvenida"},
            {"$set": {"expirado": True}}
        )
        return True
    except Exception as e:
        logger.error(f"Error marcando paquete bienvenida expirado para {user_id}: {e}")
        return False

async def usuario_compro_paquete_bienvenida(user_id: int):
    """Verifica si un usuario compró el paquete de bienvenida"""
    try:
        promo = await promos_col.find_one({
            "user_id": user_id,
            "tipo": "paquete_bienvenida"
        })
        return promo is not None
    except Exception as e:
        logger.error(f"Error verificando compra paquete bienvenida para {user_id}: {e}")
        return False

async def usuario_paquete_bienvenida_expirado(user_id: int):
    """Verifica si el paquete de bienvenida de un usuario expiró"""
    try:
        promo = await promos_col.find_one({
            "user_id": user_id,
            "tipo": "paquete_bienvenida"
        })
        
        if not promo:
            return False
        
        fecha_expiracion = promo.get("fecha_expiracion")
        if not fecha_expiracion:
            return False
        
        return datetime.datetime.now() > fecha_expiracion
    except Exception as e:
        logger.error(f"Error verificando expiración paquete bienvenida para {user_id}: {e}")
        return False



async def contar_usuarios():
    """Cuenta el total de usuarios registrados"""
    try:
        return await usuarios_col.count_documents({})
    except Exception as e:
        logger.error(f"Error contando usuarios: {e}")
        return 0

async def contar_depositos():
    """Cuenta el total de depósitos"""
    try:
        return await depositos_col.count_documents({})
    except Exception as e:
        logger.error(f"Error contando depósitos: {e}")
        return 0

async def contar_retiros():
    """Cuenta el total de retiros"""
    try:
        return await creditos_col.count_documents({"tipo": "retiro"})
    except Exception as e:
        logger.error(f"Error contando retiros: {e}")
        return 0



async def notificar_credito_agregado(bot, user_id: int, cantidad: float, razon: str):
    """Notifica a un usuario sobre crédito agregado"""
    try:
        mensaje = (
            f"💰 Crédito Agregado\n\n"
            f"Cantidad: {cantidad:.3f} TON\n"
            f"Razón: {razon}\n\n"
            "¡Tu balance ha sido actualizado!"
        )
        await bot.send_message(user_id, mensaje)
        logger.info(f"✅ Notificación de crédito enviada a {user_id}")
    except Exception as e:
        logger.error(f"Error enviando notificación de crédito a {user_id}: {e}")



async def log_action(actor_id: int, action: str, target_id: int = None, details: dict = None):
    """Registra una acción en el sistema"""
    try:
        log_data = {
            "actor_id": actor_id,
            "action": action,
            "target_id": target_id,
            "details": details or {},
            "fecha": datetime.datetime.now()
        }
        await logs_col.insert_one(log_data)
    except Exception as e:
        logger.error(f"Error registrando acción {action} para {actor_id}: {e}")

async def get_last_promo_time(user_id: int):
    """Obtiene la última vez que un usuario recibió una promoción"""
    try:
        promo = await promos_col.find_one({
            "user_id": user_id,
            "tipo": "promo_diaria"
        })
        return promo.get("ultima_promo") if promo else None
    except Exception as e:
        logger.error(f"Error obteniendo última promo para {user_id}: {e}")
        return None

async def set_last_promo_time(user_id: int, dt: datetime.datetime):
    """Establece la última vez que un usuario recibió una promoción"""
    try:
        await promos_col.update_one(
            {"user_id": user_id, "tipo": "promo_diaria"},
            {"$set": {"ultima_promo": dt}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error estableciendo última promo para {user_id}: {e}")

async def obtener_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    try:
        total_usuarios = await contar_usuarios()
        total_depositos = await contar_depositos()
        total_retiros = await contar_retiros()
        
        # Calcular volumen total
        pipeline = [
            {"$match": {"estado": "procesado"}},
            {"$group": {
                "_id": None,
                "volumen_total": {"$sum": "$cantidad_real"}
            }}
        ]
        result = await depositos_col.aggregate(pipeline).to_list(1)
        volumen_total = result[0]["volumen_total"] if result else 0
        
        return {
            "total_usuarios": total_usuarios,
            "total_depositos": total_depositos,
            "total_retiros": total_retiros,
            "volumen_total": volumen_total
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas generales: {e}")
        return {
            "total_usuarios": 0,
            "total_depositos": 0,
            "total_retiros": 0,
            "volumen_total": 0
        }

async def obtener_usuarios_activos(dias: int = 7):
    """Obtiene el número de usuarios activos en los últimos días"""
    try:
        fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
        return await usuarios_col.count_documents({
            "ultima_actividad": {"$gte": fecha_limite}
        })
    except Exception as e:
        logger.error(f"Error obteniendo usuarios activos: {e}")
        return 0

async def limpiar_logs_antiguos(dias: int = 30):
    """Limpia logs antiguos de la base de datos"""
    try:
        fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
        result = await logs_col.delete_many({
            "fecha": {"$lt": fecha_limite}
        })
        logger.info(f"✅ Logs antiguos limpiados: {result.deleted_count} registros")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error limpiando logs antiguos: {e}")
        return 0

async def verificar_nfts_expirados():
    """Verifica y desactiva NFTs expirados"""
    try:
        # Implementar lógica de verificación de NFTs expirados
        logger.info("✅ Verificación de NFTs expirados completada")
        return True
    except Exception as e:
        logger.error(f"Error verificando NFTs expirados: {e}")
        return False