from utils.database import notificar_recompensa, contar_referidos, contar_referidos_activos, usuarios_col, log_action

async def otorgar_hada_si_corresponde(bot, user_id):
    total = await contar_referidos(user_id)
    if total > 0 and total % 10 == 0:
        await notificar_recompensa(bot, user_id, "hada")
        # Sumar el hada al inventario
        usuario = await usuarios_col.find_one({"user_id": user_id})
        inventario = usuario.get("inventario", {}) if usuario else {}
        inventario["hada"] = inventario.get("hada", 0) + 1
        await usuarios_col.update_one({"user_id": user_id}, {"$set": {"inventario": inventario}})
        await log_action(user_id, "recompensa_otorgada", details={"tipo": "hada", "cantidad": 1, "motivo": "10 referidos"})

async def otorgar_elfo_si_corresponde(bot, user_id):
    activos = await contar_referidos_activos(user_id)
    if activos > 0:
        await notificar_recompensa(bot, user_id, "elfo")
        # Sumar el elfo al inventario
        usuario = await usuarios_col.find_one({"user_id": user_id})
        inventario = usuario.get("inventario", {}) if usuario else {}
        inventario["elfo"] = inventario.get("elfo", 0) + 1
        await usuarios_col.update_one({"user_id": user_id}, {"$set": {"inventario": inventario}})
        await log_action(user_id, "recompensa_otorgada", details={"tipo": "elfo", "cantidad": 1, "motivo": "referido activo"}) 