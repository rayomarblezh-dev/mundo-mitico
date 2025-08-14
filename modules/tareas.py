import re
import datetime
import logging
import unicodedata
from typing import Dict, List, Optional, Tuple
from aiogram import types, Bot, BaseMiddleware
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import usuarios_col

logger = logging.getLogger(__name__)

# Configuración
MUNDO_MITICO_VARIANTS = ["mundo mitico", "mundomitico", "mundo mítico", "mundomítico"]
REF_LINK_REGEX = re.compile(r"t\.me/\w+\?start=ref_\d+")

TAREAS_CONFIG = {
    "ref_bio": {
        "3_dias": {"hadas": 1, "mensaje": "¡Has recibido 1 hada por tener tu enlace de referido en la bio durante 3 días!"},
        "7_dias": {"hadas": 3, "mensaje": "¡Has recibido 3 hadas por tener tu enlace de referido en la bio durante 7 días!"}
    },
    "mundo_nombre": {
        "10_dias": {"hadas": 5, "mensaje": "¡Has recibido 5 hadas por tener 'Mundo Mitico' en tu nombre durante 10 días!"}
    }
}

def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    return unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8').lower()

def contiene_mundo_mitico(nombre: str) -> bool:
    nombre_normalizado = normalizar_texto(nombre)
    return any(variant in nombre_normalizado for variant in MUNDO_MITICO_VARIANTS)

def crear_teclado_tareas() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Update", callback_data="actualizar_tareas")
    builder.button(text="« Back", callback_data="perfil")
    builder.adjust(2)
    return builder.as_markup()

async def tareas_handler(event) -> None:
    """Handler principal de tareas (funciona con mensajes y callbacks)"""
    if not hasattr(event, 'from_user'):
        return
    
    user_id = event.from_user.id
    is_callback = hasattr(event, 'data')

    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            await event.answer("❌ User not found")
            return
        
        mensaje = await generar_mensaje_tareas(user_id, usuario)
        keyboard = crear_teclado_tareas()

        if is_callback:
            try:
                await event.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
            except Exception as e:
                if "message is not modified" not in str(e):
                    await event.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            await event.answer()
        else:
            await event.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en tareas_handler para user_id={user_id}: {e}")
        await event.answer("❌ Error loading tasks", show_alert=True)

async def verificar_tareas_handler(callback: types.CallbackQuery) -> None:
    """Handler para actualizar tareas manualmente"""
    user_id = callback.from_user.id
    
    try:
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            await callback.answer("❌ Usuario no encontrado", show_alert=True)
            return
        
        cambios = await check_tareas_usuario(
            callback.bot,
            user_id,
            usuario.get("username", ""),
            usuario.get("first_name", "")
        )

        # Recargar usuario para obtener tareas e inventario actualizados
        usuario = await usuarios_col.find_one({"user_id": user_id})
        mensaje_actualizado = await generar_mensaje_tareas(user_id, usuario)
        keyboard = crear_teclado_tareas()

        try:
            await callback.message.edit_text(mensaje_actualizado, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            if "message is not modified" not in str(e):
                await callback.message.answer(mensaje_actualizado, parse_mode="HTML", reply_markup=keyboard)
        
        if cambios:
            await callback.answer("✅ Rewards claimed!", show_alert=True)
        else:
            await callback.answer("ℹ️ No changes in your tasks.\n\nMake sure to:\n• Add referral link to your bio\n• Add 'Mundo Mitico' to your name", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error en verificar_tareas_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error updating tasks", show_alert=True)

async def generar_mensaje_tareas(user_id: int, usuario: Dict) -> str:
    """Genera el mensaje principal de tareas"""
    tareas = usuario.get("tareas", {})
        
    mensaje = (
        "<b>📋 Tasks</b>\n\n"
        "Complete these tasks to earn rewards:\n\n"
    )

    mensaje += await generar_info_tarea_ref_bio(tareas)
    mensaje += await generar_info_tarea_mundo_nombre(tareas)

    mensaje += "💡 Press 'Update' to check your progress."

    return mensaje

async def generar_info_tarea_ref_bio(tareas: Dict, usuario: Dict) -> str:
    """Genera información de la tarea de enlace de referido en bio"""
    tarea_ref = tareas.get("ref_bio", {})

    if tarea_ref.get("inicio"):
        dias_ref = (datetime.datetime.now() - tarea_ref["inicio"]).days
        recompensas_ref = tarea_ref.get("recompensas", [])
        texto = "<b>1️⃣ Referral Link</b>\n"
        texto += f"Progress: {dias_ref} days\n"
        texto += "Rewards:\n"
        texto += "• 3 days: 1 Fairy"
        if 1 in recompensas_ref:
            texto += " ✅"
        texto += "\n"
        texto += "• 7 days: 3 Fairies"
        if 3 in recompensas_ref:
            texto += " ✅"
        texto += "\n\n"
    else:
        texto = (
            "<b>1️⃣ Referral Link</b>\n"
            f"Bio: {usuario.get('bio', 'No bio found')}\n"
            f"Name: {usuario.get('first_name', 'No name found')}\n"
            "Status: Not started\n"
            "Rewards: 1 Fairy (3 days) / 3 Fairies (7 days)\n\n"
        )

    return texto

async def generar_info_tarea_mundo_nombre(tareas: Dict, usuario: Dict) -> str:
    """Genera información de la tarea de 'Mundo Mitico' en nombre"""
    tarea_nombre = tareas.get("mundo_nombre", {})

    if tarea_nombre.get("inicio"):
        dias_nombre = (datetime.datetime.now() - tarea_nombre["inicio"]).days
        recompensas_nombre = tarea_nombre.get("recompensas", [])
        texto = "<b>2️⃣ 'Mundo Mitico' in Name</b>\n"
        texto += f"Progress: {dias_nombre} days\n"
        texto += "Rewards:\n"
        texto += "• 10 days: 5 Fairies"
        if 5 in recompensas_nombre:
            texto += " ✅"
        texto += "\n\n"
    else:
        texto = (
            "<b>2️⃣ 'Mundo Mitico' in Name</b>\n"
            f"Name: {usuario.get('first_name', 'No name found')}\n"
            f"Bio: {usuario.get('bio', 'No bio found')}\n"
            "Status: Not started\n"
            "Rewards: 5 Fairies (10 days)\n\n"
        )

    return texto

# =========================
# MIDDLEWARE
# =========================

class MundoMiticoNombreMiddleware(BaseMiddleware):
    """
    Middleware para detectar nombres que contienen 'Mundo Mitico'
    y verificar tareas automáticamente.
    """

    async def __call__(self, handler, event, data):
        user = getattr(event, 'from_user', None)
        if user:
            # Verificar nombre
            nombre_usuario = f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'username', '') or ''}".strip()
            if contiene_mundo_mitico(nombre_usuario):
                await self._procesar_nombre_mundo_mitico(user, nombre_usuario, event)

            # Ejecutar revisión de tareas
            await self._verificar_tareas_automaticas(event, user)

        return await handler(event, data)

    async def _procesar_nombre_mundo_mitico(self, user, nombre_usuario: str, event) -> None:
        """Procesa cuando se detecta 'Mundo Mitico' en el nombre."""
        logger.info(f"[MUNDO_MITICO] Usuario {user.id} tiene 'Mundo Mitico' en su nombre: {nombre_usuario}")

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

        # Ya no notificamos al usuario para evitar spam

    async def _notificar_deteccion(self, event, user) -> None:
        """Notifica al usuario sobre la detección (ya no se usa)."""
        # Esta función ya no se usa para evitar spam
        pass

    async def _verificar_tareas_automaticas(self, event, user) -> None:
        """Verifica tareas automáticamente."""
        try:
                await check_tareas_usuario(
                    event.bot,
                    user.id,
                    getattr(user, 'username', ''),
                    getattr(user, 'first_name', '')
                )
        except Exception as e:
            logger.warning(f"Error en check_tareas_usuario para user_id={user.id}: {e}")

# =========================
# FUNCIONES DE VERIFICACIÓN DE TAREAS
# =========================

async def check_tareas_usuario(bot: Bot, user_id: int, username: str, first_name: str) -> bool:
    """
    Verifica y procesa tareas del usuario.

    Args:
        bot: Instancia del bot
        user_id: ID del usuario
        username: Username del usuario
        first_name: Nombre del usuario

    Returns:
        True si hubo cambios, False en caso contrario
    """
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return False

    # Obtener información actual del chat
    chat_info = await _obtener_info_chat(bot, user_id)
    if not chat_info:
        return False

    nombre_actual, bio_actual = chat_info
    now = datetime.datetime.now()
    tareas = usuario.get("tareas", {})
    inventario = usuario.get("inventario", {})
    cambios = False

    # Verificar tarea de enlace en bio
    cambios |= await _verificar_tarea_ref_bio(bot, user_id, bio_actual, tareas, inventario, now)

    # Verificar tarea de nombre
    cambios |= await _verificar_tarea_mundo_nombre(bot, user_id, nombre_actual, tareas, inventario, now)

    # Guardar cambios si hubo
    if cambios:
        await _guardar_cambios_tareas(user_id, tareas, inventario)
        logger.info(f"✅ Tareas actualizadas para user_id={user_id}")

    return cambios

async def _obtener_info_chat(bot: Bot, user_id: int) -> Optional[Tuple[str, str]]:
    """
    Obtiene información del chat del usuario.

    Args:
        bot: Instancia del bot
        user_id: ID del usuario

    Returns:
        Tupla con (nombre, bio) o None si hay error
    """
    try:
        chat = await bot.get_chat(user_id)
        nombre_actual = f"{chat.first_name or ''} {chat.last_name or ''}".strip()
        bio_actual = (chat.bio or "").lower()
        return nombre_actual, bio_actual
    except Exception as e:
        logger.warning(f"No se pudo obtener el chat de user_id={user_id}: {e}")
        return None

async def _verificar_tarea_ref_bio(bot: Bot, user_id: int, bio_actual: str, tareas: Dict, inventario: Dict, now: datetime.datetime) -> bool:
    """
    Verifica la tarea de enlace de referido en bio.

    Returns:
        True si hubo cambios, False en caso contrario
    """
    tiene_ref = bool(REF_LINK_REGEX.search(bio_actual))
    tarea_ref = tareas.get("ref_bio", {})
    cambios = False

    if tiene_ref:
        if not tarea_ref.get("inicio"):
            tarea_ref = {"inicio": now, "recompensas": []}
            cambios = True
        else:
            dias = (now - tarea_ref["inicio"]).days
            cambios |= await _procesar_recompensas_ref_bio(bot, user_id, dias, tarea_ref, inventario)
    else:
        # Si la condición se pierde, reiniciar
        if tarea_ref.get("inicio"):
            tarea_ref = {}
            cambios = True

    tareas["ref_bio"] = tarea_ref
    return cambios

async def _verificar_tarea_mundo_nombre(bot: Bot, user_id: int, nombre_actual: str, tareas: Dict, inventario: Dict, now: datetime.datetime) -> bool:
    """
    Verifica la tarea de "Mundo Mitico" en nombre.

    Returns:
        True si hubo cambios, False en caso contrario
    """
    nombre_normalizado = normalizar_texto(nombre_actual)
    tiene_mundo = any(v in nombre_normalizado for v in MUNDO_MITICO_VARIANTS)
    tarea_nombre = tareas.get("mundo_nombre", {})
    cambios = False

    if tiene_mundo:
        if not tarea_nombre.get("inicio"):
            tarea_nombre = {"inicio": now, "recompensas": []}
            cambios = True
        else:
            dias = (now - tarea_nombre["inicio"]).days
            cambios |= await _procesar_recompensas_mundo_nombre(bot, user_id, dias, tarea_nombre, inventario)
    else:
        if tarea_nombre.get("inicio"):
            tarea_nombre = {}
            cambios = True

    tareas["mundo_nombre"] = tarea_nombre
    return cambios

async def _procesar_recompensas_ref_bio(bot: Bot, user_id: int, dias: int, tarea_ref: Dict, inventario: Dict) -> bool:
    """
    Procesa recompensas de la tarea de enlace en bio.

    Returns:
        True si se entregó alguna recompensa
    """
    cambios = False
    recompensas = tarea_ref.get("recompensas", [])

    # Recompensa de 3 días
    if 3 <= dias < 7 and 1 not in recompensas:
        config = TAREAS_CONFIG["ref_bio"]["3_dias"]
        inventario["hada"] = inventario.get("hada", 0) + config["hadas"]
        recompensas.append(1)
        await _enviar_notificacion_recompensa(bot, user_id, config["mensaje"])
        cambios = True

    # Recompensa de 7 días
    if dias >= 7 and 3 not in recompensas:
        config = TAREAS_CONFIG["ref_bio"]["7_dias"]
        inventario["hada"] = inventario.get("hada", 0) + config["hadas"]
        recompensas.append(3)
        await _enviar_notificacion_recompensa(bot, user_id, config["mensaje"])
        cambios = True

    tarea_ref["recompensas"] = recompensas
    return cambios

async def _procesar_recompensas_mundo_nombre(bot: Bot, user_id: int, dias: int, tarea_nombre: Dict, inventario: Dict) -> bool:
    """
    Procesa recompensas de la tarea de nombre.

    Returns:
        True si se entregó alguna recompensa
    """
    cambios = False
    recompensas = tarea_nombre.get("recompensas", [])

    # Recompensa de 10 días
    if dias >= 10 and 5 not in recompensas:
        config = TAREAS_CONFIG["mundo_nombre"]["10_dias"]
        inventario["hada"] = inventario.get("hada", 0) + config["hadas"]
        recompensas.append(5)
        await _enviar_notificacion_recompensa(bot, user_id, config["mensaje"])
        cambios = True

    tarea_nombre["recompensas"] = recompensas
    return cambios

async def _enviar_notificacion_recompensa(bot: Bot, user_id: int, mensaje: str) -> None:
    """
    Envía notificación de recompensa al usuario.

    Args:
        bot: Instancia del bot
        user_id: ID del usuario
        mensaje: Mensaje a enviar
    """
    try:
        # Enviar emoji en un mensaje separado
        await bot.send_message(user_id, "🎉")

        # Enviar texto en otro mensaje
        texto_sin_emoji = mensaje.replace("🎉 ", "").replace("🎉", "")
        await bot.send_message(user_id, texto_sin_emoji)

    except Exception as e:
        logger.warning(f"Error al enviar mensaje de recompensa a {user_id}: {e}")

async def _guardar_cambios_tareas(user_id: int, tareas: Dict, inventario: Dict) -> None:
    """
    Guarda los cambios de tareas en la base de datos.

    Args:
        user_id: ID del usuario
        tareas: Tareas actualizadas
        inventario: Inventario actualizado
    """
    try:
            await usuarios_col.update_one(
                {"user_id": user_id},
                {"$set": {"tareas": tareas, "inventario": inventario}}
            )
    except Exception as e:
            logger.error(f"Error al actualizar usuario {user_id} en la base de datos: {e}")
    
# =========================
# REGISTRO DE HANDLERS
# =========================

def register_tareas_handlers(dp) -> None:
    """Registra todos los handlers del módulo tareas"""
    # Callbacks principales
    dp.callback_query.register(verificar_tareas_handler, lambda c: c.data == "actualizar_tareas")
    dp.callback_query.register(tareas_handler, lambda c: c.data == "tareas")