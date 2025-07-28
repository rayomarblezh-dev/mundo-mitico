import random
import datetime
import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import (
    usuarios_col, 
    obtener_inventario_usuario, 
    descontar_balance_usuario,
    log_action
)
from modules.constants import COOLDOWNS_EXPLORAR, RECOMPENSAS_CAJA_SORPRESA

logger = logging.getLogger(__name__)

# Configuración de cooldowns (en horas) - usando constantes centralizadas
COOLDOWNS = COOLDOWNS_EXPLORAR

# Configuración de recompensas - usando constantes centralizadas
RECOMPENSAS_PELEA = {
    "nada": {"probabilidad": 30, "mensaje": "💥 Perdiste la pelea. Mejora tu estrategia."},
    "ganar": {"probabilidad": 70, "mensaje": "🏆 ¡Victoria! Ganaste 0.1 TON", "ton": 0.1}
}

RECOMPENSAS_EXPEDICION = {
    "nada": {"probabilidad": 50, "mensaje": "🗺️ La expedición no encontró nada valioso."},
    "hada": {"probabilidad": 40, "mensaje": "🎉 ¡La expedición encontró 1 Hada!", "item": "hada", "cantidad": 1},
    "ton": {"probabilidad": 10, "mensaje": "💰 ¡La expedición encontró 0.05 TON!", "ton": 0.05}
}

RECOMPENSAS_CAPTURAR = {
    "nada": {"probabilidad": 70, "mensaje": "⚔️ La criatura se escapó. Intenta de nuevo."},
    "hada": {"probabilidad": 25, "mensaje": "🎉 ¡Capturaste 1 Hada!", "item": "hada", "cantidad": 1},
    "elfo": {"probabilidad": 5, "mensaje": "🎉 ¡Capturaste 1 Elfo!", "item": "elfo", "cantidad": 1}
}

async def explorar_handler(event):
    """Handler principal del módulo explorar (funciona con mensajes y callbacks)"""
    # Determinar si es un mensaje o callback
    if hasattr(event, 'from_user'):
        user_id = event.from_user.id
        is_callback = hasattr(event, 'data')
    else:
        return
    
    # Obtener inventario del usuario
    inventario = await obtener_inventario_usuario(user_id)
    
    mensaje = (
        "🌍 Explorar\n\n"
        "Bienvenido a las tierras salvajes de Mundo Mítico! Aquí puedes embarcarte en aventuras épicas, encontrar tesoros ocultos y capturar criaturas legendarias.\n\n"
        "Actividades disponibles:\n"
        "• Caja Sorpresa - Descubre tesoros aleatorios (0.05 TON)\n"
        "• Pelea - Enfréntate en combate (requiere 3 Licántropos)\n"
        "• Expedición - Explora territorios desconocidos (requiere 1 Elfo + 1 Genio + 1 Orco)\n"
        "• Capturar Criatura - Atrapa bestias míticas (requiere 1 Licántropo + 2 Orcos)\n\n"
        "Cooldowns:\n"
        "• Pelea: 48 horas\n"
        "• Expedición: 48 horas\n"
        "• Capturar: 24 horas"
    )
    
    # Crear teclado con las opciones
    builder = InlineKeyboardBuilder()
    builder.button(text="🎁 Caja Sorpresa", callback_data="explorar_caja_sorpresa")
    builder.button(text="⚔️ Pelea", callback_data="explorar_pelea")
    builder.button(text="🗺️ Expedición", callback_data="explorar_expedicion")
    builder.button(text="🏹 Capturar", callback_data="explorar_capturar")
    builder.button(text="⏰ Cooldowns", callback_data="explorar_cooldowns")
    builder.button(text="🔙 Volver", callback_data="start_volver")
    builder.adjust(1, 2, 1, 1, 1)
    
    keyboard = builder.as_markup()
    
    # Enviar mensaje según el tipo de evento
    if is_callback:
        try:
            await event.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            if "message is not modified" in str(e):
                # El mensaje es el mismo, solo responder al callback
                pass
            else:
                # Otro error, intentar enviar nuevo mensaje
                await event.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await event.answer()
    else:
        await event.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def verificar_cooldown(user_id: int, actividad: str) -> tuple[bool, datetime.datetime]:
    """Verifica si el usuario puede realizar una actividad basado en el cooldown"""
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return True, None
    
    cooldowns = usuario.get("cooldowns", {})
    ultima_actividad = cooldowns.get(actividad)
    
    if not ultima_actividad:
        return True, None
    
    # Convertir string a datetime si es necesario
    if isinstance(ultima_actividad, str):
        ultima_actividad = datetime.datetime.fromisoformat(ultima_actividad.replace('Z', '+00:00'))
    
    tiempo_transcurrido = datetime.datetime.now() - ultima_actividad
    cooldown_horas = COOLDOWNS.get(actividad, 24)
    
    if tiempo_transcurrido.total_seconds() < cooldown_horas * 3600:
        tiempo_restante = (cooldown_horas * 3600) - tiempo_transcurrido.total_seconds()
        return False, ultima_actividad + datetime.timedelta(seconds=cooldown_horas * 3600)
    
    return True, None

async def actualizar_cooldown(user_id: int, actividad: str):
    """Actualiza el cooldown de una actividad para el usuario"""
    await usuarios_col.update_one(
        {"user_id": user_id},
        {"$set": {f"cooldowns.{actividad}": datetime.datetime.now()}}
    )

async def obtener_recompensa_aleatoria(recompensas: dict) -> dict:
    """Obtiene una recompensa aleatoria basada en las probabilidades"""
    numero = random.randint(1, 100)
    acumulado = 0
    
    for recompensa, config in recompensas.items():
        acumulado += config["probabilidad"]
        if numero <= acumulado:
            return config
    
    # Fallback a "nada" si algo sale mal
    return recompensas["nada"]

async def agregar_item_inventario(user_id: int, item: str, cantidad: int = 1):
    """Agrega un item al inventario del usuario"""
    await usuarios_col.update_one(
        {"user_id": user_id},
        {"$inc": {f"inventario.{item}": cantidad}}
    )

async def agregar_ton_usuario(user_id: int, cantidad: float):
    """Agrega TON al balance del usuario"""
    await usuarios_col.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": cantidad}}
    )

async def caja_sorpresa_handler(callback: types.CallbackQuery):
    """Handler para la caja sorpresa"""
    user_id = callback.from_user.id
    
    # Verificar balance
    usuario = await usuarios_col.find_one({"user_id": user_id})
    balance = float(usuario.get("balance", 0)) if usuario else 0.0
    if not usuario or balance < 0.05:
        await callback.answer("❌ Necesitas: 0.05 TON", show_alert=True)
        return
    
    # Descontar TON
    if not await descontar_balance_usuario(user_id, 0.05):
        await callback.answer("❌ Error al procesar el pago", show_alert=True)
        return
    
    # Obtener recompensa
    recompensa = await obtener_recompensa_aleatoria(RECOMPENSAS_CAJA_SORPRESA)
    
    # Procesar recompensa
    if "item" in recompensa:
        await agregar_item_inventario(user_id, recompensa["item"], recompensa["cantidad"])
        mensaje = f"{recompensa['mensaje']}\n\n✅ {recompensa['cantidad']} {recompensa['item'].title()} agregado(s) a tu inventario"
    elif "ton" in recompensa:
        await agregar_ton_usuario(user_id, recompensa["ton"])
        mensaje = f"{recompensa['mensaje']}\n\n✅ {recompensa['ton']} TON agregado(s) a tu balance"
    else:
        mensaje = recompensa['mensaje']
    
    # Log de la acción
    await log_action(user_id, "caja_sorpresa", details={
        "costo": 0.05,
        "recompensa": recompensa
    })
    
    # Botón para volver
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="explorar")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
    ])
    
    try:
        # Enviar emoji en un mensaje separado
        await callback.message.answer("🎁")
        # Enviar texto en otro mensaje
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    
    await callback.answer()

async def pelea_handler(callback: types.CallbackQuery):
    """Handler para la pelea"""
    user_id = callback.from_user.id
    
    # Verificar inventario
    inventario = await obtener_inventario_usuario(user_id)
    licantropos = inventario.get("licantropo", 0)
    
    if licantropos < 3:
        await callback.answer(
            f"❌ Necesitas 3 Licántropos\n🧳 Tienes: {licantropos}", 
            show_alert=True
        )
        return
    
    # Verificar cooldown
    puede_pelear, tiempo_fin = await verificar_cooldown(user_id, "pelea")
    if not puede_pelear:
        tiempo_restante = tiempo_fin - datetime.datetime.now()
        horas = int(tiempo_restante.total_seconds() // 3600)
        minutos = int((tiempo_restante.total_seconds() % 3600) // 60)
        await callback.answer(
            f"⏰ Cooldown activo. Puedes pelear en {horas}h {minutos}m", 
            show_alert=True
        )
        return
    
    # Actualizar cooldown
    await actualizar_cooldown(user_id, "pelea")
    
    # Obtener resultado de la pelea
    recompensa = await obtener_recompensa_aleatoria(RECOMPENSAS_PELEA)
    
    if "ton" in recompensa:
        await agregar_ton_usuario(user_id, recompensa["ton"])
        mensaje = f"{recompensa['mensaje']}\n\n✅ {recompensa['ton']} TON agregado(s) a tu balance"
    else:
        mensaje = recompensa['mensaje']
    
    # Log de la acción
    await log_action(user_id, "pelea", details={
        "licantropos_usados": 3,
        "recompensa": recompensa
    })
    
    # Botón para volver
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="explorar")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
    ])
    
    try:
        # Enviar emoji en un mensaje separado
        await callback.message.answer("⚔️")
        # Enviar texto en otro mensaje
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    
    await callback.answer()

async def expedicion_handler(callback: types.CallbackQuery):
    """Handler para la expedición"""
    user_id = callback.from_user.id
    
    # Verificar inventario
    inventario = await obtener_inventario_usuario(user_id)
    elfos = inventario.get("elfo", 0)
    genios = inventario.get("genio", 0)
    orcos = inventario.get("orco", 0)
    
    if elfos < 1 or genios < 1 or orcos < 1:
        await callback.answer(
            f"❌ Necesitas: 1 Elfo, 1 Genio y 1 Orco\n"
            f"🧳 Tienes: {elfos} Elfos, {genios} Genios, {orcos} Orcos", 
            show_alert=True
        )
        return
    
    # Verificar cooldown
    puede_expedicion, tiempo_fin = await verificar_cooldown(user_id, "expedicion")
    if not puede_expedicion:
        tiempo_restante = tiempo_fin - datetime.datetime.now()
        horas = int(tiempo_restante.total_seconds() // 3600)
        minutos = int((tiempo_restante.total_seconds() % 3600) // 60)
        await callback.answer(
            f"⏰ Cooldown activo. Puedes hacer expedición en {horas}h {minutos}m", 
            show_alert=True
        )
        return
    
    # Actualizar cooldown
    await actualizar_cooldown(user_id, "expedicion")
    
    # Obtener resultado de la expedición
    recompensa = await obtener_recompensa_aleatoria(RECOMPENSAS_EXPEDICION)
    
    if "item" in recompensa:
        await agregar_item_inventario(user_id, recompensa["item"], recompensa["cantidad"])
        mensaje = f"{recompensa['mensaje']}\n\n✅ {recompensa['cantidad']} {recompensa['item'].title()} agregado(s) a tu inventario"
    elif "ton" in recompensa:
        await agregar_ton_usuario(user_id, recompensa["ton"])
        mensaje = f"{recompensa['mensaje']}\n\n✅ {recompensa['ton']} TON agregado(s) a tu balance"
    else:
        mensaje = recompensa['mensaje']
    
    # Log de la acción
    await log_action(user_id, "expedicion", details={
        "requisitos": {"elfo": 1, "genio": 1, "orco": 1},
        "recompensa": recompensa
    })
    
    # Botón para volver
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="explorar")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
    ])
    
    try:
        # Enviar emoji en un mensaje separado
        await callback.message.answer("🗺️")
        # Enviar texto en otro mensaje
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    
    await callback.answer()

async def capturar_handler(callback: types.CallbackQuery):
    """Handler para capturar criatura mística"""
    user_id = callback.from_user.id
    
    # Verificar inventario
    inventario = await obtener_inventario_usuario(user_id)
    licantropos = inventario.get("licantropo", 0)
    orcos = inventario.get("orco", 0)
    
    if licantropos < 1 or orcos < 2:
        await callback.answer(
            f"❌ Necesitas: 1 Licántropo y 2 Orcos\n"
            f"🧳 Tienes: {licantropos} Licántropos, {orcos} Orcos", 
            show_alert=True
        )
        return
    
    # Verificar cooldown
    puede_capturar, tiempo_fin = await verificar_cooldown(user_id, "capturar")
    if not puede_capturar:
        tiempo_restante = tiempo_fin - datetime.datetime.now()
        horas = int(tiempo_restante.total_seconds() // 3600)
        minutos = int((tiempo_restante.total_seconds() % 3600) // 60)
        await callback.answer(
            f"⏰ Cooldown activo. Puedes capturar en {horas}h {minutos}m", 
            show_alert=True
        )
        return
    
    # Actualizar cooldown
    await actualizar_cooldown(user_id, "capturar")
    
    # Obtener resultado de la captura
    recompensa = await obtener_recompensa_aleatoria(RECOMPENSAS_CAPTURAR)
    
    if "item" in recompensa:
        await agregar_item_inventario(user_id, recompensa["item"], recompensa["cantidad"])
        mensaje = f"{recompensa['mensaje']}\n\n✅ {recompensa['cantidad']} {recompensa['item'].title()} agregado(s) a tu inventario"
    else:
        mensaje = recompensa['mensaje']
    
    # Log de la acción
    await log_action(user_id, "capturar_criatura", details={
        "requisitos": {"licantropo": 1, "orco": 2},
        "recompensa": recompensa
    })
    
    # Botón para volver
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="explorar")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
    ])
    
    try:
        # Enviar emoji en un mensaje separado
        await callback.message.answer("🏹")
        # Enviar texto en otro mensaje
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    
    await callback.answer()

async def mostrar_cooldowns_handler(callback: types.CallbackQuery):
    """Handler para mostrar cooldowns actuales"""
    user_id = callback.from_user.id
    
    usuario = await usuarios_col.find_one({"user_id": user_id})
    cooldowns = usuario.get("cooldowns", {}) if usuario else {}
    
    mensaje = "⏰ Cooldowns Actuales\n\n"
    
    ahora = datetime.datetime.now()
    actividades = ["pelea", "expedicion", "capturar"]
    
    for actividad in actividades:
        ultima_actividad = cooldowns.get(actividad)
        if ultima_actividad:
            # Convertir string a datetime si es necesario
            if isinstance(ultima_actividad, str):
                ultima_actividad = datetime.datetime.fromisoformat(ultima_actividad.replace('Z', '+00:00'))
            
            tiempo_transcurrido = ahora - ultima_actividad
            cooldown_horas = COOLDOWNS.get(actividad, 24)
            
            if tiempo_transcurrido.total_seconds() < cooldown_horas * 3600:
                tiempo_restante = (cooldown_horas * 3600) - tiempo_transcurrido.total_seconds()
                horas = int(tiempo_restante // 3600)
                minutos = int((tiempo_restante % 3600) // 60)
                mensaje += f"• {actividad.title()}: {horas}h {minutos}m restantes\n"
            else:
                mensaje += f"• {actividad.title()}: ✅ Disponible\n"
        else:
            mensaje += f"• {actividad.title()}: ✅ Disponible\n"
    
    mensaje += "\n<i>Los cooldowns se reinician automáticamente cuando expiran.</i>"
    
    # Botón para volver
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="explorar")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
    ])
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    
    await callback.answer()



def register_explorar_handlers(dp):
    """Registra todos los handlers del módulo explorar"""
    # Callbacks principales
    dp.callback_query.register(caja_sorpresa_handler, lambda c: c.data == "explorar_caja_sorpresa")
    dp.callback_query.register(pelea_handler, lambda c: c.data == "explorar_pelea")
    dp.callback_query.register(expedicion_handler, lambda c: c.data == "explorar_expedicion")
    dp.callback_query.register(capturar_handler, lambda c: c.data == "explorar_capturar")
    dp.callback_query.register(mostrar_cooldowns_handler, lambda c: c.data == "explorar_cooldowns")
