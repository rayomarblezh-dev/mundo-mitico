import re
import datetime
import logging
import unicodedata
from aiogram import types, Bot, BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import (
    usuarios_col, 
    agregar_item_inventario,
    obtener_inventario_usuario,
    contar_referidos,
    contar_referidos_activos
)

logger = logging.getLogger(__name__)

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

# Expresión regular para detectar el enlace de referido
REF_LINK_REGEX = re.compile(r"t\.me/\w+\?start=ref_\d+")

async def tareas_handler(event):
    """Handler principal de tareas (funciona con mensajes y callbacks)"""
    # Determinar si es un mensaje o callback
    if hasattr(event, 'from_user'):
        user_id = event.from_user.id
        is_callback = hasattr(event, 'data')
    else:
        return
    
    try:
        # Obtener información del usuario
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            await event.answer("❌ Usuario no encontrado")
            return
        
        # Obtener inventario para mostrar recompensas
        inventario = await obtener_inventario_usuario(user_id)
        hadas = inventario.get("hada", 0)
        elfos = inventario.get("elfo", 0)
        
        # Obtener estadísticas de referidos
        total_referidos = await contar_referidos(user_id)
        referidos_activos = await contar_referidos_activos(user_id)
        
        # Obtener información de tareas
        tareas = usuario.get("tareas", {})
        
        mensaje = (
            "📋 Tareas Diarias\n\n"
            "Completa estas tareas para obtener recompensas exclusivas:\n\n"
        )
        
        # Tarea 1: Enlace de referido en bio
        tarea_ref = tareas.get("ref_bio", {})
        if tarea_ref.get("inicio"):
            dias_ref = (datetime.datetime.now() - tarea_ref["inicio"]).days
            recompensas_ref = tarea_ref.get("recompensas", [])
            
            mensaje += "🔗 Enlace de Referido en Bio:\n"
            mensaje += f"   Progreso: {dias_ref} días\n"
            mensaje += "   Recompensas:\n"
            mensaje += "   • 3 días: 1 Hada"
            if 1 in recompensas_ref:
                mensaje += " ✅"
            mensaje += "\n"
            mensaje += "   • 7 días: 3 Hadas"
            if 3 in recompensas_ref:
                mensaje += " ✅"
            mensaje += "\n\n"
        else:
            mensaje += "🔗 Enlace de Referido en Bio:\n"
            mensaje += "   Estado: No iniciado\n"
            mensaje += "   Recompensas: 1 Hada (3 días) / 3 Hadas (7 días)\n\n"
        
        # Tarea 2: "Mundo Mitico" en nombre
        tarea_nombre = tareas.get("mundo_nombre", {})
        if tarea_nombre.get("inicio"):
            dias_nombre = (datetime.datetime.now() - tarea_nombre["inicio"]).days
            recompensas_nombre = tarea_nombre.get("recompensas", [])
            
            mensaje += "🏷️ 'Mundo Mitico' en Nombre:\n"
            mensaje += f"   Progreso: {dias_nombre} días\n"
            mensaje += "   Recompensas:\n"
            mensaje += "   • 10 días: 5 Hadas"
            if 5 in recompensas_nombre:
                mensaje += " ✅"
            mensaje += "\n\n"
        else:
            mensaje += "🏷️ 'Mundo Mitico' en Nombre:\n"
            mensaje += "   Estado: No iniciado\n"
            mensaje += "   Recompensas: 5 Hadas (10 días)\n\n"
        
        # Tarea 3: Referidos
        mensaje += "👥 Referidos:\n"
        mensaje += f"   Total: {total_referidos}\n"
        mensaje += f"   Activos: {referidos_activos}\n"
        mensaje += "   Recompensas:\n"
        mensaje += "   • 10 referidos: 1 Hada\n"
        mensaje += "   • Por cada activo: 1 Elfo\n\n"
        
        # Mostrar inventario actual
        mensaje += f"🎁 Tu Inventario:\n"
        mensaje += f"   Hadas: {hadas}\n"
        mensaje += f"   Elfos: {elfos}\n\n"
        
        mensaje += "💡 Consejo: Las tareas se verifican automáticamente cada vez que usas el bot."
        
        # Crear teclado
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Verificar Tareas", callback_data="verificar_tareas")
        builder.button(text="📊 Ver Progreso", callback_data="progreso_tareas")
        builder.button(text="🔙 Volver", callback_data="start_volver")
        builder.adjust(2, 1)
        keyboard = builder.as_markup()
        
        # Enviar mensaje según el tipo de evento
        if is_callback:
            try:
                await event.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
            except Exception as e:
                if "message is not modified" in str(e):
                    pass
                else:
                    await event.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            await event.answer()
        else:
            await event.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en tareas_handler para user_id={user_id}: {e}")
        await event.answer("❌ Error al cargar tareas", show_alert=True)

async def verificar_tareas_handler(callback: types.CallbackQuery):
    """Handler para verificar tareas manualmente"""
    user_id = callback.from_user.id
    
    try:
        # Obtener información del usuario
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            await callback.answer("❌ Usuario no encontrado", show_alert=True)
            return
        
        # Verificar tareas
        cambios = await check_tareas_usuario(callback.bot, user_id, usuario.get("username", ""), usuario.get("first_name", ""))
        
        if cambios:
            await callback.answer("✅ Tareas verificadas. ¡Revisa si obtuviste recompensas!", show_alert=True)
        else:
            await callback.answer("ℹ️ No hay cambios en tus tareas", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error en verificar_tareas_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al verificar tareas", show_alert=True)

async def progreso_tareas_handler(callback: types.CallbackQuery):
    """Handler para mostrar progreso detallado de tareas"""
    user_id = callback.from_user.id
    
    try:
        # Obtener información del usuario
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            await callback.answer("❌ Usuario no encontrado", show_alert=True)
            return
        
        tareas = usuario.get("tareas", {})
        
        mensaje = "📊 Progreso Detallado de Tareas\n\n"
        
        # Progreso de enlace en bio
        tarea_ref = tareas.get("ref_bio", {})
        if tarea_ref.get("inicio"):
            dias_ref = (datetime.datetime.now() - tarea_ref["inicio"]).days
            mensaje += f"🔗 Enlace en Bio: {dias_ref} días\n"
            if dias_ref >= 3:
                mensaje += "   ✅ Recompensa de 3 días disponible\n"
            if dias_ref >= 7:
                mensaje += "   ✅ Recompensa de 7 días disponible\n"
        else:
            mensaje += "🔗 Enlace en Bio: No iniciado\n"
        
        # Progreso de nombre
        tarea_nombre = tareas.get("mundo_nombre", {})
        if tarea_nombre.get("inicio"):
            dias_nombre = (datetime.datetime.now() - tarea_nombre["inicio"]).days
            mensaje += f"🏷️ Nombre con 'Mundo Mitico': {dias_nombre} días\n"
            if dias_nombre >= 10:
                mensaje += "   ✅ Recompensa de 10 días disponible\n"
        else:
            mensaje += "🏷️ Nombre con 'Mundo Mitico': No iniciado\n"
        
        # Botón para volver
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tareas")]
        ])
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error en progreso_tareas_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al mostrar progreso", show_alert=True)

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
                        await event.answer("🎉 ¡Tu nombre contiene 'Mundo Mitico'!", show_alert=True)
                    except Exception as e:
                        logging.warning(f"Error al enviar alerta a usuario {user.id}: {e}")
                elif hasattr(event, 'message'):
                    try:
                        await event.message.answer("🎉 ¡Tu nombre contiene 'Mundo Mitico'!")
                    except Exception as e:
                        logging.warning(f"Error al enviar mensaje a usuario {user.id}: {e}")
            # Ejecutar revisión de tareas (nombre y bio)
            try:
                await check_tareas_usuario(
                    event.bot,
                    user.id,
                    getattr(user, 'username', ''),
                    getattr(user, 'first_name', '')
                )
            except Exception as e:
                logging.warning(f"Error en check_tareas_usuario para user_id={user.id}: {e}")
        return await handler(event, data)

async def check_tareas_usuario(bot: Bot, user_id: int, username: str, first_name: str):
    """Verificar y procesar tareas del usuario"""
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return False

    # Obtener nombre y bio actual
    try:
        chat = await bot.get_chat(user_id)
    except Exception as e:
        logging.warning(f"No se pudo obtener el chat de user_id={user_id}: {e}")
        return False

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
                    await bot.send_message(user_id, "🎉 ¡Has recibido 1 hada por tener tu enlace de referido en la bio durante 3 días!")
                except Exception as e:
                    logging.warning(f"Error al enviar mensaje de recompensa (1 hada) a {user_id}: {e}")
                cambios = True
            # 7 días - 3 hadas
            if dias >= 7 and 3 not in tarea_ref.get("recompensas", []):
                inventario["hada"] = inventario.get("hada", 0) + 3
                tarea_ref.setdefault("recompensas", []).append(3)
                try:
                    await bot.send_message(user_id, "🎉 ¡Has recibido 3 hadas por tener tu enlace de referido en la bio durante 7 días!")
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
                    await bot.send_message(user_id, "🎉 ¡Has recibido 5 hadas por tener 'Mundo Mitico' en tu nombre durante 10 días!")
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
            logger.info(f"✅ Tareas actualizadas para user_id={user_id}")
        except Exception as e:
            logger.error(f"Error al actualizar usuario {user_id} en la base de datos: {e}")
    
    return cambios

def register_tareas_handlers(dp):
    """Registra todos los handlers del módulo tareas"""
    # Callbacks principales
    dp.callback_query.register(verificar_tareas_handler, lambda c: c.data == "verificar_tareas")
    dp.callback_query.register(progreso_tareas_handler, lambda c: c.data == "progreso_tareas")
    dp.callback_query.register(tareas_handler, lambda c: c.data == "tareas")