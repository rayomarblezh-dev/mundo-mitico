import logging
from utils.database import notificar_recompensa, contar_referidos, contar_referidos_activos, usuarios_col, log_action

logger = logging.getLogger(__name__)

async def otorgar_hada_si_corresponde(bot, user_id):
    """Otorga una hada si el usuario tiene múltiplos de 10 referidos"""
    try:
        total = await contar_referidos(user_id)
        if total > 0 and total % 10 == 0:
            await notificar_recompensa(bot, user_id, "hada")
            # Sumar el hada al inventario
            usuario = await usuarios_col.find_one({"user_id": user_id})
            inventario = usuario.get("inventario", {}) if usuario else {}
            inventario["hada"] = inventario.get("hada", 0) + 1
            await usuarios_col.update_one({"user_id": user_id}, {"$set": {"inventario": inventario}})
            await log_action(user_id, "recompensa_otorgada", details={"tipo": "hada", "cantidad": 1, "motivo": "10 referidos"})
            logger.info(f"✅ Hada otorgada a user_id={user_id} por {total} referidos")
    except Exception as e:
        logger.error(f"❌ Error otorgando hada a user_id={user_id}: {e}")

async def otorgar_elfo_si_corresponde(bot, user_id):
    """Otorga un elfo si el usuario tiene referidos activos"""
    try:
        activos = await contar_referidos_activos(user_id)
        if activos > 0:
            await notificar_recompensa(bot, user_id, "elfo")
            # Sumar el elfo al inventario
            usuario = await usuarios_col.find_one({"user_id": user_id})
            inventario = usuario.get("inventario", {}) if usuario else {}
            inventario["elfo"] = inventario.get("elfo", 0) + 1
            await usuarios_col.update_one({"user_id": user_id}, {"$set": {"inventario": inventario}})
            await log_action(user_id, "recompensa_otorgada", details={"tipo": "elfo", "cantidad": 1, "motivo": "referido activo"})
            logger.info(f"✅ Elfo otorgado a user_id={user_id} por {activos} referidos activos")
    except Exception as e:
        logger.error(f"❌ Error otorgando elfo a user_id={user_id}: {e}") 