from utils.database import notificar_recompensa, contar_referidos, contar_referidos_activos

async def otorgar_hada_si_corresponde(bot, user_id):
    total = await contar_referidos(user_id)
    if total > 0 and total % 10 == 0:
        await notificar_recompensa(bot, user_id, "hada")
        # Aquí puedes agregar lógica para sumar el hada al inventario

async def otorgar_elfo_si_corresponde(bot, user_id):
    activos = await contar_referidos_activos(user_id)
    if activos > 0:
        await notificar_recompensa(bot, user_id, "elfo")
        # Aquí puedes agregar lógica para sumar el elfo al inventario 