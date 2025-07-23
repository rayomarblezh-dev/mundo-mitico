import re
import datetime
from utils.database import usuarios_col, agregar_credito_usuario
from aiogram import Bot

# Palabras clave para detectar "Mundo Mitico" en el nombre
MUNDO_MITICO_VARIANTS = [
    "mundo mitico", "mundomitico", "mundo mítico", "mundomítico"
]

# Regex para detectar el enlace de referido
REF_LINK_REGEX = re.compile(r"t\.me/\w+\?start=ref_\d+")

async def check_tareas_usuario(bot: Bot, user_id: int, username: str, first_name: str):
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return
    # Obtener nombre y bio actual
    # NOTA: aiogram no da acceso directo a la bio, se debe usar get_chat
    chat = await bot.get_chat(user_id)
    nombre_actual = f"{chat.first_name or ''} {chat.last_name or ''}".strip().lower()
    bio_actual = (chat.bio or "").lower()
    now = datetime.datetime.now()
    tareas = usuario.get("tareas", {})
    inventario = usuario.get("inventario", {})
    cambios = False
    # --- Tarea 1: Enlace de referido en la bio ---
    tiene_ref = bool(REF_LINK_REGEX.search(bio_actual))
    tarea_ref = tareas.get("ref_bio", {})
    if tiene_ref:
        if not tarea_ref.get("inicio"):
            tarea_ref = {"inicio": now, "recompensas": []}
            cambios = True
        else:
            dias = (now - tarea_ref["inicio"]).days
            # 3 días - 1 hada
            if 3 <= dias < 7 and 1 not in tarea_ref["recompensas"]:
                inventario["hada"] = inventario.get("hada", 0) + 1
                tarea_ref["recompensas"].append(1)
                await bot.send_message(user_id, "🎁 ¡Has recibido 1 hada por tener tu enlace de referido en la bio durante 3 días!")
                cambios = True
            # 7 días - 3 hadas
            if dias >= 7 and 3 not in tarea_ref["recompensas"]:
                inventario["hada"] = inventario.get("hada", 0) + 3
                tarea_ref["recompensas"].append(3)
                await bot.send_message(user_id, "🎁 ¡Has recibido 3 hadas por tener tu enlace de referido en la bio durante 7 días!")
                cambios = True
    else:
        # Si la condición se pierde, reiniciar
        if tarea_ref.get("inicio"):
            tarea_ref = {}
            cambios = True
    tareas["ref_bio"] = tarea_ref
    # --- Tarea 2: "Mundo Mitico" en el nombre ---
    tiene_mundo = any(v in nombre_actual for v in MUNDO_MITICO_VARIANTS)
    tarea_nombre = tareas.get("mundo_nombre", {})
    if tiene_mundo:
        if not tarea_nombre.get("inicio"):
            tarea_nombre = {"inicio": now, "recompensas": []}
            cambios = True
        else:
            dias = (now - tarea_nombre["inicio"]).days
            # 10 días - 5 hadas
            if dias >= 10 and 5 not in tarea_nombre["recompensas"]:
                inventario["hada"] = inventario.get("hada", 0) + 5
                tarea_nombre["recompensas"].append(5)
                await bot.send_message(user_id, "🎁 ¡Has recibido 5 hadas por tener 'Mundo Mitico' en tu nombre durante 10 días!")
                cambios = True
    else:
        if tarea_nombre.get("inicio"):
            tarea_nombre = {}
            cambios = True
    tareas["mundo_nombre"] = tarea_nombre
    # Guardar cambios si hubo
    if cambios:
        await usuarios_col.update_one(
            {"user_id": user_id},
            {"$set": {"tareas": tareas, "inventario": inventario}}
        )