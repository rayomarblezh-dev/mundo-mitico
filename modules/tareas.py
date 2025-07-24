import re
import datetime
from utils.database import usuarios_col, agregar_credito_usuario
from aiogram import Bot
import unicodedata

# Palabras clave para detectar "Mundo Mitico" en el nombre
MUNDO_MITICO_VARIANTS = [
    "mundo mitico", "mundomitico", "mundo mítico", "mundomítico"
]

def contiene_mundo_mitico(nombre):
    # Normaliza a minúsculas y elimina tildes
    nombre = unicodedata.normalize('NFD', nombre).encode('ascii', 'ignore').decode('utf-8').lower()
    return any(variant in nombre for variant in MUNDO_MITICO_VARIANTS)

from aiogram.dispatcher.middlewares.base import BaseMiddleware
import logging
class MundoMiticoNombreMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, 'from_user', None)
        if user:
            nombre_usuario = (getattr(user, 'first_name', '') or '') + ' ' + (getattr(user, 'username', '') or '')
            if contiene_mundo_mitico(nombre_usuario):
                logging.info(f"[MUNDO_MITICO] Usuario {user.id} tiene 'Mundo Mitico' en su nombre: {nombre_usuario}")
                # Guardar registro en la base de datos
                await usuarios_col.update_one(
                    {"user_id": user.id},
                    {"$set": {"detectado_mundo_mitico": True, "nombre_detectado": nombre_usuario, "fecha_detectado": datetime.datetime.now()}},
                    upsert=True
                )
                # Notificar al usuario (si es un mensaje o callback)
                if hasattr(event, 'answer'):
                    try:
                        await event.answer("🎉 ¡Tu nombre contiene 'Mundo Mitico'!", show_alert=True)
                    except Exception:
                        pass
                elif hasattr(event, 'message'):
                    try:
                        await event.message.answer("🎉 ¡Tu nombre contiene 'Mundo Mitico'!")
                    except Exception:
                        pass
            # Ejecutar revisión de tareas (nombre y bio)
            try:
                from modules.tareas import check_tareas_usuario
                from modules.bot import bot
                await check_tareas_usuario(bot, user.id, getattr(user, 'username', ''), getattr(user, 'first_name', ''))
            except Exception as e:
                logging.warning(f"Error en check_tareas_usuario para user_id={user.id}: {e}")
        return await handler(event, data)

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