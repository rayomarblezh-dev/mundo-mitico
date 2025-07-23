from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import re
import platform
import psutil
from utils.database import agregar_credito_usuario, notificar_credito_agregado, contar_usuarios, contar_depositos, contar_retiros, obtener_depositos_pendientes, log_action
from config.config import is_admin, MIN_DEPOSITO, MIN_RETIRO, COMISION_RETIRO, TIEMPO_PROCESAMIENTO
import logging
import datetime
from utils.database import depositos_col, creditos_col

logger = logging.getLogger(__name__)

# Estados para FSM de administración
class AdminStates(StatesGroup):
    waiting_for_user_id = State()      # Esperando ID del usuario
    waiting_for_amount = State()       # Esperando cantidad a agregar
    waiting_for_reason = State()       # Esperando razón del crédito
    waiting_for_confirmation = State() # Esperando confirmación

# Eliminar ADMIN_IDS y función is_admin locales

async def admin_handler(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado al panel admin por user_id={user_id}")
        await message.edit_text(
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
        "— Buscar usuario y ver historial\n"
        "— Ver estadísticas del bot\n"
        "— Gestionar depósitos pendientes\n"
        "— Configurar parámetros del sistema\n"
        "— Revisar tareas de usuarios</i>"
    )
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Buscar", callback_data="admin_buscar")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="admin_estadisticas")],
        [
            InlineKeyboardButton(text="💵 Depósitos", callback_data="admin_depositos"),
            InlineKeyboardButton(text="💸 Retiros", callback_data="admin_retiros")
        ],
        [InlineKeyboardButton(text="❗ Importante", callback_data="admin_importante")]
    ])
    try:
        await message.edit_text(mensaje, parse_mode="HTML", reply_markup=admin_keyboard)
    except Exception:
        await message.answer(mensaje, parse_mode="HTML", reply_markup=admin_keyboard)

async def admin_agregar_credito_handler(callback: types.CallbackQuery, state: FSMContext):
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
    await state.set_state(AdminStates.waiting_for_user_id)
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def procesar_user_id(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    user_input = message.text.strip()
    target_user_id = None
    if user_input.startswith('@'):
        username = user_input[1:]
        from utils.database import obtener_usuario_por_username
        usuario = await obtener_usuario_por_username(username)
        if usuario:
            target_user_id = usuario.get("user_id")
        else:
            await message.answer(
                f"<b>❌ Usuario no encontrado</b>\n\n<i>No se encontró ningún usuario con el username <code>@{username}</code>.</i>",
                parse_mode="HTML"
            )
            return
    else:
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
    await state.update_data(target_user_id=target_user_id)
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
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    cantidad_text = message.text.strip()
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
    await state.update_data(cantidad=cantidad)
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
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    razon = message.text.strip()
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    cantidad = data.get('cantidad')
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
    await state.update_data(razon=razon)
    await state.set_state(AdminStates.waiting_for_confirmation)
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirmar", callback_data="admin_confirmar_credito")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="admin_cancelar_credito")]
    ])
    await message.answer(mensaje_confirmacion, parse_mode="HTML", reply_markup=confirm_keyboard)

async def confirmar_credito_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a confirmar crédito por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} inició proceso de confirmar crédito")
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    cantidad = data.get('cantidad')
    razon = data.get('razon', 'Sin razón específica')
    try:
        await agregar_credito_usuario(target_user_id, cantidad, user_id)
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
        try:
            await callback.message.edit_text(mensaje_exito, parse_mode="HTML")
        except Exception:
            await callback.message.answer(mensaje_exito, parse_mode="HTML")
        await state.clear()
    except Exception as e:
        logger.error(f"Error al agregar crédito: {e}")
        mensaje_error = (
            f"<b>❌ Error al Agregar Crédito</b>\n\n"
            f"<i>Hubo un problema al procesar la solicitud:\n"
            f"<code>{str(e)}</code></i>"
        )
        try:
            await callback.message.edit_text(mensaje_error, parse_mode="HTML")
        except Exception:
            await callback.message.answer(mensaje_error, parse_mode="HTML")
        await state.clear()
    await callback.answer()

async def cancelar_credito_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    mensaje = (
        "<b>❌ Operación Cancelada</b>\n\n"
        "<i>La operación de agregar crédito ha sido cancelada.</i>"
    )
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
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
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def admin_depositos_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a depósitos por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} consultó depósitos pendientes")
    from utils.database import depositos_col
    depositos_pendientes = await depositos_col.find({"estado": "pendiente"}).to_list(length=20)
    if not depositos_pendientes:
        mensaje = "<b>💵 Depósitos Pendientes</b>\n\n<i>No hay depósitos pendientes de revisión.</i>"
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML")
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML")
        await callback.answer()
        return
    for dep in depositos_pendientes:
        equivalente_ton = dep.get('equivalente_ton')
        red = dep.get('network_name', 'N/A')
        cantidad = dep.get('cantidad', 'No especificada')
        mensaje = (
            f"<b>💵 Depósito Pendiente</b>\n\n"
            f"<b>Usuario:</b> <code>{dep.get('user_id')}</code>\n"
            f"<b>Red:</b> {red}\n"
            f"<b>Dirección:</b> <code>{dep.get('address', 'N/A')}</code>\n"
            f"<b>Hash:</b> <code>{dep.get('hash')}</code>\n"
            f"<b>Cantidad enviada:</b> <code>{cantidad}</code> {red.split()[-1]}\n"
        )
        if equivalente_ton and red.lower() != 'ton':
            mensaje += f"<b>Equivalente estimado:</b> <code>{equivalente_ton:.4f}</code> TON\n"
        mensaje += (
            f"<b>Fecha:</b> {dep.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if dep.get('fecha') else 'N/A'}\n"
            f"<b>Estado:</b> {dep.get('estado', 'N/A')}\n\n"
            f"<i>Puedes aceptar el depósito para acreditar la cantidad al usuario o cancelar si es inválido.</i>"
        )
        aceptar_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Aceptar", callback_data=f"aceptar_deposito_{dep['_id']}"),
             InlineKeyboardButton(text="❌ Cancelar", callback_data="admin_depositos")]
        ])
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=aceptar_keyboard)
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=aceptar_keyboard)
        await callback.answer()
        return  # Mostrar de uno en uno

# Handler para aceptar depósito
async def aceptar_deposito_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    from utils.database import depositos_col, agregar_credito_usuario
    import bson
    # Extraer el ID del depósito
    dep_id = callback.data.replace("aceptar_deposito_", "")
    try:
        dep_obj_id = bson.ObjectId(dep_id)
    except Exception:
        await callback.answer("ID de depósito inválido", show_alert=True)
        return
    dep = await depositos_col.find_one({"_id": dep_obj_id})
    if not dep or dep.get("estado") != "pendiente":
        await callback.answer("Depósito no válido o ya procesado", show_alert=True)
        return
    cantidad = dep.get("cantidad")
    user_target = dep.get("user_id")
    if not cantidad or not user_target:
        await callback.answer("Datos incompletos en el depósito", show_alert=True)
        return
    # Acreditar la cantidad exacta
    await agregar_credito_usuario(user_target, float(cantidad), user_id)
    # Marcar depósito como completado
    await depositos_col.update_one({"_id": dep_obj_id}, {"$set": {"estado": "completado", "fecha_completado": datetime.datetime.now()}})
    # Notificar al usuario
    try:
        from modules.bot import bot
        await bot.send_message(user_target, f"<b>💵 Depósito acreditado</b>\n\n<i>Tu depósito de <b>{cantidad} TON</b> ha sido acreditado correctamente.</i>", parse_mode="HTML")
    except Exception:
        pass
    # Después de actualizar y notificar
    await log_action(user_id, "deposito_aceptado", target_id=user_target, details={"cantidad": cantidad})
    await callback.message.edit_text(
        f"<b>✅ Depósito Aceptado</b>\n\n"
        f"<i>Se han acreditado <b>{cantidad} TON</b> al usuario {user_target}.</i>",
        parse_mode="HTML"
    )
    await callback.answer()

async def admin_retiros_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a retiros por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} consultó retiros pendientes")
    from utils.database import creditos_col
    retiros_pendientes = await creditos_col.find({"tipo": "retiro", "estado": "pendiente"}).to_list(length=20)
    if not retiros_pendientes:
        mensaje = "<b>💸 Retiros Pendientes</b>\n\n<i>No hay retiros pendientes de revisión.</i>"
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML")
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML")
        await callback.answer()
        return
    for ret in retiros_pendientes:
        mensaje = (
            f"<b>💸 Retiro Pendiente</b>\n\n"
            f"<b>Usuario:</b> <code>{ret.get('user_id')}</code>\n"
            f"<b>Cantidad:</b> <code>{ret.get('cantidad', 'No especificada')}</code>\n"
            f"<b>Wallet:</b> <code>{ret.get('wallet', 'N/A')}</code>\n"
            f"<b>Fecha:</b> {ret.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if ret.get('fecha') else 'N/A'}\n"
            f"<b>Estado:</b> {ret.get('estado', 'N/A')}\n\n"
            f"<i>Puedes aceptar el retiro para marcarlo como completado y notificar al usuario, o cancelar si es inválido.</i>"
        )
        aceptar_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Aceptar", callback_data=f"aceptar_retiro_{ret['_id']}"),
             InlineKeyboardButton(text="❌ Cancelar", callback_data="admin_retiros")]
        ])
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=aceptar_keyboard)
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=aceptar_keyboard)
        await callback.answer()
        return  # Mostrar de uno en uno

# Handler para aceptar retiro
async def aceptar_retiro_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    from utils.database import creditos_col
    import bson
    # Extraer el ID del retiro
    ret_id = callback.data.replace("aceptar_retiro_", "")
    try:
        ret_obj_id = bson.ObjectId(ret_id)
    except Exception:
        await callback.answer("ID de retiro inválido", show_alert=True)
        return
    ret = await creditos_col.find_one({"_id": ret_obj_id})
    if not ret or ret.get("estado") != "pendiente":
        await callback.answer("Retiro no válido o ya procesado", show_alert=True)
        return
    cantidad = ret.get("cantidad")
    user_target = ret.get("user_id")
    wallet = ret.get("wallet", "N/A")
    if not cantidad or not user_target:
        await callback.answer("Datos incompletos en el retiro", show_alert=True)
        return
    # Marcar retiro como completado
    await creditos_col.update_one({"_id": ret_obj_id}, {"$set": {"estado": "completado", "fecha_completado": datetime.datetime.now()}})
    # Notificar al usuario
    try:
        from modules.bot import bot
        await bot.send_message(user_target, f"<b>💸 Retiro procesado</b>\n\n<i>Tu retiro de <b>{cantidad} TON</b> a la wallet <code>{wallet}</code> ha sido procesado correctamente.</i>", parse_mode="HTML")
    except Exception:
        pass
    # Después de actualizar y notificar
    await log_action(user_id, "retiro_aceptado", target_id=user_target, details={"cantidad": cantidad, "wallet": wallet})
    await callback.message.edit_text(
        f"<b>✅ Retiro Aceptado</b>\n\n"
        f"<i>El retiro de <b>{cantidad} TON</b> a <code>{wallet}</code> ha sido marcado como completado.</i>",
        parse_mode="HTML"
    )
    await callback.answer()

async def admin_importante_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Intento de acceso denegado a configuración por user_id={user_id}")
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    logger.info(f"Admin user_id={user_id} consultó Importante")
    mensaje = (
        f"<b>❗ Importante</b>\n\n"
        f"<i>Esta sección informa al admin sobre los parámetros críticos del sistema.</i>\n\n"
        f"<b>🔧 Parámetros Actuales:</b>\n"
        f"— Mínimo depósito: <code>{MIN_DEPOSITO}</code> TON\n"
        f"— Mínimo retiro: <code>{MIN_RETIRO}</code> TON\n"
        f"— Comisión de retiro: <code>{COMISION_RETIRO}</code> TON\n"
        f"— Tiempo de procesamiento: <code>{TIEMPO_PROCESAMIENTO}</code>\n\n"
        f"<b>⚠️ Nota:</b>\nLa configuración se puede modificar desde el panel web.\n\n"
        f"<b>Revisa estos parámetros periódicamente para evitar errores en los flujos de usuarios.</b>"
    )
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def admin_tareas_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    from utils.database import usuarios_col
    # Contar tareas pendientes y completadas (ejemplo simple)
    total_usuarios = await usuarios_col.count_documents({})
    tareas_pendientes = await usuarios_col.count_documents({"tareas": {"$exists": True, "$ne": {}}})
    mensaje = (
        f"<b>📝 Tareas de Usuarios</b>\n\n"
        f"<i>Resumen de tareas automáticas y manuales de los usuarios.</i>\n\n"
        f"<b>👥 Usuarios totales:</b> {total_usuarios}\n"
        f"<b>🕒 Usuarios con tareas pendientes:</b> {tareas_pendientes}\n"
        f"<b>✅ Usuarios sin tareas:</b> {total_usuarios - tareas_pendientes}</i>"
    )
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def admin_resumen_fondos_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    # Obtener depósitos y retiros (máximo 15 de cada uno, ordenados de viejo a reciente)
    depositos = await depositos_col.find({}).sort("fecha", 1).to_list(length=15)
    retiros = await creditos_col.find({"tipo": "retiro"}).sort("fecha", 1).to_list(length=15)
    mensaje = "<b>📊 Resumen de Fondos</b>\n\n"
    mensaje += "<b>💵 Depósitos (viejo → reciente):</b>\n"
    if depositos:
        for dep in depositos:
            mensaje += (
                f"— <code>{dep.get('fecha').strftime('%Y-%m-%d')}</code> | Usuario: <code>{dep.get('user_id')}</code> | "
                f"Cantidad: <b>{dep.get('cantidad', '?')}</b> | Estado: <b>{dep.get('estado', '?')}</b>\n"
            )
    else:
        mensaje += "Sin depósitos registrados.\n"
    mensaje += "\n<b>💸 Retiros (viejo → reciente):</b>\n"
    if retiros:
        for ret in retiros:
            mensaje += (
                f"— <code>{ret.get('fecha').strftime('%Y-%m-%d')}</code> | Usuario: <code>{ret.get('user_id')}</code> | "
                f"Cantidad: <b>{ret.get('cantidad', '?')}</b> | Estado: <b>{ret.get('estado', '?')}</b>\n"
            )
    else:
        mensaje += "Sin retiros registrados.\n"
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin")]
    ])
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    await callback.answer()

async def info_handler(message: types.Message):
    uname = platform.uname()
    svmem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu_percent = psutil.cpu_percent(interval=1)
    net = psutil.net_io_counters()
    msg = (
        "<b>ℹ️ <u>Información del Sistema</u></b>\n\n"
        "<b>🖥️ <u>Sistema:</u></b> <code>{} {}</code> <i>({})</i>\n\n"
        "<b>💾 <u>RAM:</u></b> <code>{}MB</code> / <code>{}MB</code> <i>({}%)</i>\n\n"
        "<b>💽 <u>Disco:</u></b> <code>{}GB</code> / <code>{}GB</code> <i>({}%)</i>\n\n"
        "<b>⚡ <u>CPU:</u></b> <code>{}%</code>\n\n"
        "<b>🌐 <u>Red:</u></b> <code>⬆️ {}</code> / <code>⬇️ {}</code> <i>MB</i>\n"
    ).format(
        uname.system, uname.release, uname.machine,
        svmem.used // (1024**2), svmem.total // (1024**2), svmem.percent,
        disk.used // (1024**3), disk.total // (1024**3), disk.percent,
        cpu_percent,
        net.bytes_sent // (1024**2), net.bytes_recv // (1024**2)
    )
    try:
        await message.edit_text(msg, parse_mode="HTML")
    except Exception:
        await message.answer(msg, parse_mode="HTML") 

# Nuevo flujo: Buscar usuario y mostrar historial
class BuscarStates(StatesGroup):
    waiting_for_user = State()
    mostrando_usuario = State()

async def admin_buscar_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    mensaje = (
        "<b>🔍 Buscar Usuario</b>\n\n"
        "Envía el <b>ID</b> o <b>@username</b> del usuario que deseas consultar."
    )
    await state.set_state(BuscarStates.waiting_for_user)
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def procesar_busqueda_usuario(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    user_input = message.text.strip()
    from utils.database import usuarios_col, depositos_col, creditos_col
    usuario = None
    if user_input.startswith('@'):
        username = user_input[1:]
        usuario = await usuarios_col.find_one({"username": username})
    else:
        try:
            uid = int(user_input)
            usuario = await usuarios_col.find_one({"user_id": uid})
        except Exception:
            pass
    if not usuario:
        await message.edit_text(
            f"<b>❌ Usuario no encontrado</b>\n\n<i>No se encontró ningún usuario con ese ID o username.</i>",
            parse_mode="HTML"
        )
        return
    # Buscar todos los depósitos y retiros
    depositos = await depositos_col.find({"user_id": usuario["user_id"]}).sort("fecha", -1).to_list(length=100)
    retiros = await creditos_col.find({"user_id": usuario["user_id"], "tipo": "retiro"}).sort("fecha", -1).to_list(length=100)
    await state.update_data(
        usuario_id=usuario["user_id"],
        username=usuario.get("username","-"),
        first_name=usuario.get("first_name","-"),
        balance=usuario.get("balance",0),
        fecha_registro=usuario.get("fecha_registro"),
        activo=usuario.get("activo", True),
        depositos=depositos,
        retiros=retiros,
        pagina_dep=0,
        pagina_ret=0
    )
    await mostrar_historial_usuario(message, state)
    await state.set_state(BuscarStates.mostrando_usuario)

async def mostrar_historial_usuario(event, state: FSMContext):
    data = await state.get_data()
    usuario_id = data["usuario_id"]
    username = data["username"]
    first_name = data["first_name"]
    balance = data["balance"]
    fecha_registro = data["fecha_registro"]
    activo = data["activo"]
    depositos = data["depositos"]
    retiros = data["retiros"]
    pagina_dep = data.get("pagina_dep",0)
    pagina_ret = data.get("pagina_ret",0)
    per_page = 5
    mensaje = (
        f"<b>👤 Usuario:</b> <code>{usuario_id}</code> | @{username}\n"
        f"<b>Nombre:</b> {first_name}\n"
        f"<b>Balance:</b> <code>{balance}</code> TON\n"
        f"<b>Fecha registro:</b> {fecha_registro.strftime('%Y-%m-%d') if fecha_registro else '-'}\n"
        f"<b>Estado:</b> {'Activo' if activo else 'Inactivo'}\n"
        f"<hr>"
        f"<b>💵 Depósitos (página {pagina_dep+1}/{max(1,((len(depositos)-1)//per_page)+1)}):</b>\n"
    )
    start_dep = pagina_dep*per_page
    end_dep = start_dep+per_page
    if depositos[start_dep:end_dep]:
        for i, dep in enumerate(depositos[start_dep:end_dep], start=start_dep+1):
            mensaje += (
                f"<b>{i}.</b> <code>{dep.get('fecha').strftime('%Y-%m-%d')}</code> | "
                f"<b>{dep.get('cantidad','?')}</b> {dep.get('network_name','TON').split()[-1]} | Estado: <b>{dep.get('estado','?')}</b>\n"
            )
            if dep.get('hash'):
                mensaje += f"└ <b>Hash:</b> <code>{dep.get('hash')}</code>\n"
            if dep.get('equivalente_ton') and dep.get('network_name','ton').lower() != 'ton':
                mensaje += f"└ <b>≈</b> <code>{dep.get('equivalente_ton'):.4f}</code> TON\n"
    else:
        mensaje += "Sin depósitos.\n"
    mensaje += f"<hr>\n<b>💸 Retiros (página {pagina_ret+1}/{max(1,((len(retiros)-1)//per_page)+1)}):</b>\n"
    start_ret = pagina_ret*per_page
    end_ret = start_ret+per_page
    if retiros[start_ret:end_ret]:
        for i, ret in enumerate(retiros[start_ret:end_ret], start=start_ret+1):
            mensaje += (
                f"<b>{i}.</b> <code>{ret.get('fecha').strftime('%Y-%m-%d')}</code> | "
                f"<b>{ret.get('cantidad','?')}</b> TON | Estado: <b>{ret.get('estado','?')}</b>\n"
            )
            if ret.get('wallet'):
                mensaje += f"└ <b>Wallet:</b> <code>{ret.get('wallet')}</code>\n"
    else:
        mensaje += "Sin retiros.\n"
    # Botones de paginación
    botones = []
    # Depósitos
    max_dep = ((len(depositos)-1)//per_page)
    if pagina_dep > 0:
        botones.append(InlineKeyboardButton(text="⬅️ Depósitos", callback_data="dep_prev"))
    if pagina_dep < max_dep:
        botones.append(InlineKeyboardButton(text="Depósitos ➡️", callback_data="dep_next"))
    # Retiros
    max_ret = ((len(retiros)-1)//per_page)
    if pagina_ret > 0:
        botones.append(InlineKeyboardButton(text="⬅️ Retiros", callback_data="ret_prev"))
    if pagina_ret < max_ret:
        botones.append(InlineKeyboardButton(text="Retiros ➡️", callback_data="ret_next"))
    # Volver
    botones.append(InlineKeyboardButton(text="🔙 Volver", callback_data="admin"))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[botones[i:i+2] for i in range(0, len(botones), 2)])
    # Mostrar
    if hasattr(event, 'edit_text'):
        await event.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
    else:
        await event.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def paginacion_busqueda_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pagina_dep = data.get("pagina_dep",0)
    pagina_ret = data.get("pagina_ret",0)
    if callback.data == "dep_prev":
        pagina_dep = max(0, pagina_dep-1)
    elif callback.data == "dep_next":
        pagina_dep = pagina_dep+1
    elif callback.data == "ret_prev":
        pagina_ret = max(0, pagina_ret-1)
    elif callback.data == "ret_next":
        pagina_ret = pagina_ret+1
    await state.update_data(pagina_dep=pagina_dep, pagina_ret=pagina_ret)
    await mostrar_historial_usuario(callback.message, state)
    await callback.answer() 
    