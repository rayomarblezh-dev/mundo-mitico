import re
import datetime
import logging
import unicodedata
from aiogram import Bot
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from utils.database import usuarios_col, agregar_credito_usuario

# Palabras clave para detectar "Mundo Mitico" en el nombre
MUNDO_MITICO_VARIANTS = [
    "mundo mitico", "mundomitico", "mundo mítico", "mundomítico"
]

def normalizar_texto(texto: str) -> str:
    """Normaliza el texto a minúsculas y elimina tildes."""
    if not texto:
        return ""
    return unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8').lower()

def contiene_mundo_mitico(nombre: str) -> bool:
    """Verifica si el nombre contiene alguna variante de 'Mundo Mitico'."""
    nombre_normalizado = normalizar_texto(nombre)
    return any(variant in nombre_normalizado for variant in MUNDO_MITICO_VARIANTS)

class MundoMiticoNombreMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, 'from_user', None)
        if user:
            nombre_usuario = f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'username', '') or ''}".strip()
            if contiene_mundo_mitico(nombre_usuario):
                logging.info(f"[MUNDO_MITICO] Usuario {user.id} tiene 'Mundo Mitico' en su nombre: {nombre_usuario}")
                # Guardar registro en la base de datos
                await usuarios_col.update_one(
                    {"user_id": user.id},
                    {"$set": {
                        "detectado_mundo_mitico": True,
                        "nombre_detectado": nombre_usuario,
                        "fecha_detectado": datetime.datetime.now()
                    }},
                    upsert=True
                )
                # Notificar al usuario (si es un mensaje o callback)
                if hasattr(event, 'answer'):
                    try:
                        await event.answer(" ¡Tu nombre contiene 'Mundo Mitico'!", show_alert=True)
                    except Exception as e:
                        logging.warning(f"Error al enviar alerta a usuario {user.id}: {e}")
                elif hasattr(event, 'message'):
                    try:
                        await event.message.answer("¡Tu nombre contiene 'Mundo Mitico'!")
                    except Exception as e:
                        logging.warning(f"Error al enviar mensaje a usuario {user.id}: {e}")
            # Ejecutar revisión de tareas (nombre y bio)
            try:
                from modules.tareas import check_tareas_usuario
                from modules.bot import bot
                await check_tareas_usuario(
                    bot,
                    user.id,
                    getattr(user, 'username', ''),
                    getattr(user, 'first_name', '')
                )
            except Exception as e:
                logging.warning(f"Error en check_tareas_usuario para user_id={user.id}: {e}")
        return await handler(event, data)

# Expresión regular para detectar el enlace de referido
REF_LINK_REGEX = re.compile(r"t\.me/\w+\?start=ref_\d+")

async def check_tareas_usuario(bot: Bot, user_id: int, username: str, first_name: str):
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return

    # Obtener nombre y bio actual
    try:
        chat = await bot.get_chat(user_id)
    except Exception as e:
        logging.warning(f"No se pudo obtener el chat de user_id={user_id}: {e}")
        return

    nombre_actual = f"{chat.first_name or ''} {chat.last_name or ''}".strip()
    nombre_actual_normalizado = normalizar_texto(nombre_actual)
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
            if 3 <= dias < 7 and 1 not in tarea_ref.get("recompensas", []):
                inventario["hada"] = inventario.get("hada", 0) + 1
                tarea_ref.setdefault("recompensas", []).append(1)
                try:
                    await bot.send_message(user_id, "🎉")
                    await bot.send_message(user_id, "🎁 ¡Has recibido 1 hada por tener tu enlace de referido en la bio durante 3 días!")
                except Exception as e:
                    logging.warning(f"Error al enviar mensaje de recompensa (1 hada) a {user_id}: {e}")
                cambios = True
            # 7 días - 3 hadas
            if dias >= 7 and 3 not in tarea_ref.get("recompensas", []):
                inventario["hada"] = inventario.get("hada", 0) + 3
                tarea_ref.setdefault("recompensas", []).append(3)
                try:
                    await bot.send_message(user_id, "🎉")
                    await bot.send_message(user_id, "🎁 ¡Has recibido 3 hadas por tener tu enlace de referido en la bio durante 7 días!")
                except Exception as e:
                    logging.warning(f"Error al enviar mensaje de recompensa (3 hadas) a {user_id}: {e}")
                cambios = True
    else:
        # Si la condición se pierde, reiniciar
        if tarea_ref.get("inicio"):
            tarea_ref = {}
            cambios = True
    tareas["ref_bio"] = tarea_ref

    # --- Tarea 2: "Mundo Mitico" en el nombre ---
    tiene_mundo = any(v in nombre_actual_normalizado for v in MUNDO_MITICO_VARIANTS)
    tarea_nombre = tareas.get("mundo_nombre", {})
    if tiene_mundo:
        if not tarea_nombre.get("inicio"):
            tarea_nombre = {"inicio": now, "recompensas": []}
            cambios = True
        else:
            dias = (now - tarea_nombre["inicio"]).days
            # 10 días - 5 hadas
            if dias >= 10 and 5 not in tarea_nombre.get("recompensas", []):
                inventario["hada"] = inventario.get("hada", 0) + 5
                tarea_nombre.setdefault("recompensas", []).append(5)
                try:
                    await bot.send_message(user_id, "🎉")
                    await bot.send_message(user_id, "🎁 ¡Has recibido 5 hadas por tener 'Mundo Mitico' en tu nombre durante 10 días!")
                except Exception as e:
                    logging.warning(f"Error al enviar mensaje de recompensa (5 hadas) a {user_id}: {e}")
                cambios = True
    else:
        if tarea_nombre.get("inicio"):
            tarea_nombre = {}
            cambios = True
    tareas["mundo_nombre"] = tarea_nombre

    # Guardar cambios si hubo
    if cambios:
        try:
            await usuarios_col.update_one(
                {"user_id": user_id},
                {"$set": {"tareas": tareas, "inventario": inventario}}
            )
        except Exception as e:
            logging.error(f"Error al actualizar usuario {user_id} en la base de datos: {e}")