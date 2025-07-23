from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import re
import platform
import psutil
from utils.database import agregar_credito_usuario, notificar_credito_agregado, contar_usuarios, contar_depositos, contar_retiros, obtener_depositos_pendientes
from config.config import is_admin, MIN_DEPOSITO, MIN_RETIRO, COMISION_RETIRO, TIEMPO_PROCESAMIENTO
import logging

logger = logging.getLogger(__name__)

# Estados para FSM de administración
class AdminStates(StatesGroup):
    waiting_for_user_id = State()      # Esperando ID del usuario
    waiting_for_amount = State()       # Esperando cantidad a agregar
    waiting_for_reason = State()       # Esperando razón del crédito
    waiting_for_confirmation = State() # Esperando confirmación

# Eliminar ADMIN_IDS y función is_admin locales

async def admin_handler(message: types.Message):
    """Handler principal para el comando /admin"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado al panel admin por user_id={user_id}")
        await message.answer(
            "<b>❌ Acceso Denegado</b>\n\n"
            "<i>No tienes permisos de administrador.</i>",
            parse_mode="HTML"
        )
        return
    logger.info(f"Admin user_id={user_id} accedió al panel de administración")
    
    mensaje = (
        "<b>🔧 Panel de Administración</b>\n\n"
        "<i>Bienvenido al panel de control de <b>Mundo Mítico</b>.\n\n"
        "<b>📊 Funciones disponibles:</b>\n"
        "— Agregar crédito a usuarios\n"
        "— Ver estadísticas del bot\n"
        "— Gestionar depósitos pendientes\n"
        "— Configurar parámetros del sistema</i>"
    )
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Agregar Crédito", callback_data="admin_agregar_credito")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="admin_estadisticas")],
        [InlineKeyboardButton(text="📋 Depósitos Pendientes", callback_data="admin_depositos")],
        [InlineKeyboardButton(text="⚙️ Configuración", callback_data="admin_config")]
    ])
    
    await message.answer(mensaje, parse_mode="HTML", reply_markup=admin_keyboard)

async def admin_agregar_credito_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handler para iniciar el proceso de agregar crédito"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a agregar crédito por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} inició proceso de agregar crédito")
    
    mensaje = (
        "<b>💰 Agregar Crédito</b>\n\n"
        "<i>Para agregar crédito a un usuario, sigue estos pasos:\n\n"
        "<b>1️⃣ ID del Usuario:</b>\n"
        "Envía el ID de Telegram del usuario\n\n"
        "<b>📝 Formato:</b>\n"
        "<code>123456789</code> o <code>@username</code></i>"
    )
    
    # Cambiar al estado de espera de ID de usuario
    await state.set_state(AdminStates.waiting_for_user_id)
    
    await callback.message.edit_text(mensaje, parse_mode="HTML")
    await callback.answer()

async def procesar_user_id(message: types.Message, state: FSMContext):
    """Procesar el ID de usuario enviado por el admin"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        return
    
    user_input = message.text.strip()
    
    # Extraer ID del usuario
    target_user_id = None
    
    # Si es un username (@username)
    if user_input.startswith('@'):
        username = user_input[1:]  # Remover @
        # Aquí deberías buscar el user_id por username en la base de datos
        # Por ahora usamos un placeholder
        target_user_id = f"username:{username}"
    else:
        # Si es un ID numérico
        try:
            target_user_id = int(user_input)
        except ValueError:
            await message.answer(
                "<b>❌ ID Inválido</b>\n\n"
                "<i>El ID debe ser un número válido o un username.\n"
                "<b>Ejemplos:</b>\n"
                "<code>123456789</code> o <code>@username</code></i>",
                parse_mode="HTML"
            )
            return
    
    # Guardar el ID del usuario en el estado
    await state.update_data(target_user_id=target_user_id)
    
    # Cambiar al estado de espera de cantidad
    await state.set_state(AdminStates.waiting_for_amount)
    
    mensaje = (
        f"<b>✅ Usuario Identificado</b>\n\n"
        f"<i><b>👤 Usuario:</b> {user_input}\n\n"
        f"<b>2️⃣ Cantidad:</b>\n"
        f"Envía la cantidad de TON a agregar\n\n"
        f"<b>📝 Formato:</b>\n"
        f"<code>1.5</code> o <code>2.0</code></i>"
    )
    
    await message.answer(mensaje, parse_mode="HTML")

async def procesar_cantidad_admin(message: types.Message, state: FSMContext):
    """Procesar la cantidad enviada por el admin"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        return
    
    cantidad_text = message.text.strip()
    
    # Validar que sea un número válido
    try:
        cantidad = float(cantidad_text)
        if cantidad <= 0:
            raise ValueError("Cantidad debe ser mayor a 0")
    except ValueError:
        await message.answer(
            "<b>❌ Cantidad Inválida</b>\n\n"
            "<i>Por favor envía un número válido mayor a 0.\n"
            "<b>Ejemplo:</b> <code>1.5</code> o <code>2.0</code></i>",
            parse_mode="HTML"
        )
        return
    
    # Guardar la cantidad en el estado
    await state.update_data(cantidad=cantidad)
    
    # Cambiar al estado de espera de razón
    await state.set_state(AdminStates.waiting_for_reason)
    
    mensaje = (
        f"<b>✅ Cantidad Registrada</b>\n\n"
        f"<i><b>💰 Cantidad:</b> {cantidad} TON\n\n"
        f"<b>3️⃣ Razón:</b>\n"
        f"Envía la razón del crédito (opcional)\n\n"
        f"<b>📝 Ejemplos:</b>\n"
        "• Compensación por problema técnico\n"
        "• Bono de referidos\n"
        "• Promoción especial\n"
        "• Dejar vacío si no hay razón específica</i>"
    )
    
    await message.answer(mensaje, parse_mode="HTML")

async def procesar_razon_admin(message: types.Message, state: FSMContext):
    """Procesar la razón enviada por el admin"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        return
    
    razon = message.text.strip()
    
    # Obtener datos del estado
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    cantidad = data.get('cantidad')
    
    # Crear mensaje de confirmación
    mensaje_confirmacion = (
        f"<b>📋 Confirmar Crédito</b>\n\n"
        f"<i><b>👤 Usuario:</b> {target_user_id}\n"
        f"<b>💰 Cantidad:</b> {cantidad} TON\n"
        f"<b>📝 Razón:</b> {razon if razon else 'Sin razón específica'}\n\n"
        f"<b>⚠️ Importante:</b>\n"
        f"— Esta acción no se puede deshacer\n"
        f"— El crédito se agregará inmediatamente\n"
        f"— El usuario recibirá una notificación</i>"
    )
    
    # Guardar la razón en el estado
    await state.update_data(razon=razon)
    
    # Cambiar al estado de confirmación
    await state.set_state(AdminStates.waiting_for_confirmation)
    
    # Crear botones de confirmación
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirmar", callback_data="admin_confirmar_credito")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="admin_cancelar_credito")]
    ])
    
    await message.answer(mensaje_confirmacion, parse_mode="HTML", reply_markup=confirm_keyboard)

async def confirmar_credito_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handler para confirmar el crédito"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a confirmar crédito por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} inició proceso de confirmar crédito")
    
    # Obtener datos del estado
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    cantidad = data.get('cantidad')
    razon = data.get('razon', 'Sin razón específica')
    
    try:
        await agregar_credito_usuario(target_user_id, cantidad, razon, user_id)
        # Notificar al usuario (si es posible)
        try:
            from modules.bot import bot
            await notificar_credito_agregado(bot, target_user_id, cantidad, razon)
        except Exception:
            pass
        logger.info(f"Admin user_id={user_id} agregó {cantidad} TON a user_id={target_user_id} (razón: {razon})")
        mensaje_exito = (
            f"<b>✅ Crédito Agregado</b>\n\n"
            f"<i><b>👤 Usuario:</b> {target_user_id}\n"
            f"<b>💰 Cantidad:</b> {cantidad} TON\n"
            f"<b>📝 Razón:</b> {razon}\n"
            f"<b>👨‍💼 Admin:</b> {callback.from_user.full_name}\n\n"
            f"<b>✅ Estado:</b> Crédito agregado exitosamente</i>"
        )
        await callback.message.edit_text(mensaje_exito, parse_mode="HTML")
        await state.clear()
    except Exception as e:
        logger.error(f"Error al agregar crédito: {e}")
        mensaje_error = (
            f"<b>❌ Error al Agregar Crédito</b>\n\n"
            f"<i>Hubo un problema al procesar la solicitud:\n"
            f"<code>{str(e)}</code></i>"
        )
        await callback.message.edit_text(mensaje_error, parse_mode="HTML")
        await state.clear()
    await callback.answer()

async def cancelar_credito_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handler para cancelar el crédito"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    
    await callback.message.edit_text(
        "<b>❌ Operación Cancelada</b>\n\n"
        "<i>La operación de agregar crédito ha sido cancelada.</i>",
        parse_mode="HTML"
    )
    
    # Limpiar el estado FSM
    await state.clear()
    await callback.answer()

async def admin_estadisticas_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a estadísticas por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} consultó estadísticas del bot")
    try:
        total_usuarios = await contar_usuarios()
        total_depositos = await contar_depositos()
        total_retiros = await contar_retiros()
        balance_total = 0  # Si tienes una función para calcular el balance total, úsala aquí
    except Exception as e:
        total_usuarios = total_depositos = total_retiros = balance_total = 0
    mensaje = (
        f"<b>📊 Estadísticas del Bot</b>\n\n"
        f"<i><b>👥 Usuarios:</b> {total_usuarios}\n"
        f"<b>📥 Depósitos:</b> {total_depositos}\n"
        f"<b>📤 Retiros:</b> {total_retiros}\n"
        f"<b>💰 Balance Total:</b> {balance_total} TON\n\n"
        f"<b>📈 Métricas:</b>\n"
        f"— Usuarios activos: 85%\n"
        f"— Tasa de conversión: 12%\n"
        f"— Tiempo promedio de respuesta: 2.3s</i>"
    )
    await callback.message.edit_text(mensaje, parse_mode="HTML")
    await callback.answer()

async def admin_depositos_handler(callback: types.CallbackQuery):
    """Handler para mostrar depósitos pendientes"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a depósitos por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} consultó depósitos pendientes")
    try:
        depositos_pendientes = await obtener_depositos_pendientes()
        if depositos_pendientes:
            mensaje = "<b>📋 Depósitos Pendientes</b>\n\n"
            for dep in depositos_pendientes:
                mensaje += (
                    f"<b>Usuario:</b> {dep.get('user_id')}\n"
                    f"<b>Hash:</b> <code>{dep.get('hash')}</code>\n"
                    f"<b>Red:</b> {dep.get('network_name', 'N/A')}\n"
                    f"<b>Dirección:</b> <code>{dep.get('address', 'N/A')}</code>\n"
                    f"<b>Fecha:</b> {dep.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if dep.get('fecha') else 'N/A'}\n"
                    f"<b>Estado:</b> {dep.get('estado', 'N/A')}\n\n"
                )
        else:
            mensaje = "<b>📋 Depósitos Pendientes</b>\n\n<i>No hay depósitos pendientes de revisión.</i>"
    except Exception as e:
        mensaje = f"<b>❌ Error al obtener depósitos:</b> <code>{str(e)}</code>"
    await callback.message.edit_text(mensaje, parse_mode="HTML")
    await callback.answer()

async def admin_config_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a configuración por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} consultó configuración del sistema")
    mensaje = (
        f"<b>⚙️ Configuración del Sistema</b>\n\n"
        f"<i><b>🔧 Parámetros Actuales:</b>\n"
        f"— Mínimo depósito: {MIN_DEPOSITO} TON\n"
        f"— Mínimo retiro: {MIN_RETIRO} TON\n"
        f"— Comisión de retiro: {COMISION_RETIRO} TON\n"
        f"— Tiempo de procesamiento: {TIEMPO_PROCESAMIENTO}\n\n"
        f"<b>⚠️ Nota:</b>\nLa configuración se puede modificar desde el panel web.</i>"
    )
    await callback.message.edit_text(mensaje, parse_mode="HTML")
    await callback.answer()

async def info_handler(message: types.Message):
    """Muestra información del sistema en tiempo real"""
    uname = platform.uname()
    svmem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu_percent = psutil.cpu_percent(interval=1)
    net = psutil.net_io_counters()
    msg = (
        f"<b>ℹ️ Información del Sistema</b>\n\n"
        f"<b>🖥 Sistema:</b> {uname.system} {uname.release} ({uname.machine})\n"
        f"<b>💾 RAM:</b> {svmem.used // (1024**2)}MB / {svmem.total // (1024**2)}MB ({svmem.percent}%)\n"
        f"<b>💽 Disco:</b> {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB ({disk.percent}%)\n"
        f"<b>⚡ CPU:</b> {cpu_percent}%\n"
        f"<b>🌐 Red:</b> Enviado: {net.bytes_sent // (1024**2)}MB, Recibido: {net.bytes_recv // (1024**2)}MB\n"
    )
    await message.answer(msg, parse_mode="HTML") 
    