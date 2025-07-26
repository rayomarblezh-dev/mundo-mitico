import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from utils.database import (
    agregar_credito_usuario, 
    procesar_retiro, 
    procesar_deposito,
    obtener_depositos_pendientes,
    obtener_retiros_pendientes,
    depositos_col,
    creditos_col,
    log_admin_action
)
from config.config import is_admin
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Estados para la máquina de estados (FSM)
class AdminStates(StatesGroup):
    esperando_cantidad_deposito = State()
    esperando_cantidad_retiro = State()

# =========================
# HANDLERS DE NOTIFICACIONES
# =========================

async def admin_deposito_notificacion_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handler para gestionar notificaciones de depósitos"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    
    # Extraer datos del callback
    data = callback.data.split("_")
    if len(data) < 4:
        await callback.answer("❌ Datos inválidos", show_alert=True)
        return
    
    accion = data[2]  # confirmar, cancelar, contactar
    deposito_id = data[3]
    
    try:
        if accion == "confirmar":
            await callback.message.edit_text(
                f"📥 Confirmar Depósito\n\n"
                f"ID: {deposito_id}\n\n"
                "Ingresa la cantidad real recibida (en TON):",
                parse_mode="HTML"
            )
            await state.set_state(AdminStates.esperando_cantidad_deposito)
            await state.update_data(deposito_id=deposito_id)
            
        elif accion == "cancelar":
            # Marcar depósito como cancelado
            await depositos_col.update_one(
                {"_id": deposito_id},
                {"$set": {"estado": "cancelado", "admin_id": callback.from_user.id}}
            )
            
            await callback.message.edit_text(
                f"❌ Depósito Cancelado\n\n"
                f"ID: {deposito_id}\n"
                "El depósito ha sido cancelado por el administrador.",
                parse_mode="HTML"
            )
            
            await log_admin_action(
                callback.from_user.id, 
                "deposito_cancelado", 
                extra={"deposito_id": deposito_id}
            )
            
        elif accion == "contactar":
            # Obtener información del depósito para el enlace
            deposito = await depositos_col.find_one({"_id": deposito_id})
            if deposito:
                user_id = deposito["user_id"]
                # Buscar username
                from utils.database import usuarios_col
                usuario = await usuarios_col.find_one({"user_id": user_id})
                username = usuario.get("username") if usuario else None
                if username:
                    contact_url = f"https://t.me/{username}"
                else:
                    contact_url = f"https://t.me/user?id={user_id}"
                await callback.message.edit_text(
                    f"💬 Contactar Usuario\n\n"
                    f"ID: {deposito_id}\n"
                    f"Usuario: {user_id}\n\n"
                    "Haz clic en el botón para contactar directamente al usuario:",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="💬 Contactar Usuario", url=contact_url)],
                        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_panel_volver")]
                    ])
                )
            else:
                await callback.answer("❌ Depósito no encontrado", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error procesando notificación de depósito: {e}")
        await callback.answer("❌ Error procesando la acción", show_alert=True)
    
    await callback.answer()

async def admin_retiro_notificacion_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handler para gestionar notificaciones de retiros"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    
    # Extraer datos del callback
    data = callback.data.split("_")
    if len(data) < 4:
        await callback.answer("❌ Datos inválidos", show_alert=True)
        return
    
    accion = data[2]  # confirmar, cancelar, contactar
    retiro_id = data[3]
    
    try:
        if accion == "confirmar":
            # Procesar retiro directamente
            ok = await procesar_retiro(retiro_id, callback.from_user.id)
            if ok:
                await callback.message.edit_text(
                    f"✅ Retiro Procesado\n\n"
                    f"ID: {retiro_id}\n"
                    "El retiro ha sido procesado exitosamente.",
                    parse_mode="HTML"
                )
            else:
                await callback.message.edit_text(
                    f"❌ Error Procesando Retiro\n\n"
                    f"ID: {retiro_id}\n"
                    "No se pudo procesar el retiro.",
                    parse_mode="HTML"
                )
                
        elif accion == "cancelar":
            # Marcar retiro como cancelado y devolver fondos
            retiro = await creditos_col.find_one({"_id": retiro_id})
            if retiro:
                # Devolver fondos al usuario
                from utils.database import agregar_balance_usuario
                await agregar_balance_usuario(retiro["user_id"], retiro["cantidad_solicitada"])
                
                # Marcar como cancelado
                await creditos_col.update_one(
                    {"_id": retiro_id},
                    {"$set": {"estado": "cancelado", "admin_id": callback.from_user.id}}
                )
                
                await callback.message.edit_text(
                    f"❌ Retiro Cancelado\n\n"
                    f"ID: {retiro_id}\n"
                    "El retiro ha sido cancelado y los fondos devueltos.",
                    parse_mode="HTML"
                )
                
                await log_admin_action(
                    callback.from_user.id, 
                    "retiro_cancelado", 
                    target_id=retiro["user_id"],
                    extra={"retiro_id": retiro_id, "cantidad_devuelta": retiro["cantidad_solicitada"]}
                )
            
        elif accion == "contactar":
            # Obtener información del retiro para el enlace
            retiro = await creditos_col.find_one({"_id": retiro_id})
            if retiro:
                user_id = retiro["user_id"]
                # Buscar username
                from utils.database import usuarios_col
                usuario = await usuarios_col.find_one({"user_id": user_id})
                username = usuario.get("username") if usuario else None
                if username:
                    contact_url = f"https://t.me/{username}"
                else:
                    contact_url = f"https://t.me/user?id={user_id}"
                await callback.message.edit_text(
                    f"💬 Contactar Usuario\n\n"
                    f"ID: {retiro_id}\n"
                    f"Usuario: {user_id}\n\n"
                    "Haz clic en el botón para contactar directamente al usuario:",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="💬 Contactar Usuario", url=contact_url)],
                        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_panel_volver")]
                    ])
                )
            else:
                await callback.answer("❌ Retiro no encontrado", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error procesando notificación de retiro: {e}")
        await callback.answer("❌ Error procesando la acción", show_alert=True)
    
    await callback.answer()

# =========================
# HANDLERS DE FSM PARA ADMIN
# =========================

async def procesar_cantidad_deposito_admin(message: types.Message, state: FSMContext):
    """Procesa la cantidad real del depósito ingresada por el admin"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        cantidad = float(message.text.strip().replace(",", "."))
        if cantidad <= 0:
            await message.answer("❌ La cantidad debe ser mayor a 0.")
            return
        
        data = await state.get_data()
        deposito_id = data.get("deposito_id")
        
        if not deposito_id:
            await message.answer("❌ Error: No se encontró el ID del depósito.")
            return
        
        # Procesar el depósito
        ok = await procesar_deposito(deposito_id, message.from_user.id, cantidad)
        
        if ok:
            await message.answer(
                f"✅ Depósito Procesado\n\n"
                f"ID: {deposito_id}\n"
                f"Cantidad: {cantidad:.3f} TON\n"
                "El depósito ha sido procesado exitosamente.",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"❌ Error Procesando Depósito\n\n"
                f"ID: {deposito_id}\n"
                "No se pudo procesar el depósito.",
                parse_mode="HTML"
            )
    
    except ValueError:
        await message.answer("❌ Por favor, ingresa un número válido.")
    except Exception as e:
        logger.error(f"Error procesando cantidad de depósito admin: {e}")
        await message.answer("❌ Error interno del sistema.")
    
    await state.clear()

# =========================
# COMANDOS DE ADMINISTRACIÓN
# =========================

async def admin_panel_handler(message: types.Message):
    """Panel principal de administración"""
    user_id = message.from_user.id
    admin_ids = __import__('config.config').config.ADMIN_IDS
    is_admin_result = is_admin(user_id)
    
    logger.info(f"Intento de acceso admin: user_id={user_id}, ADMIN_IDS={admin_ids}, is_admin()={is_admin_result}")
    
    if not is_admin_result:
        await message.answer("❌ Acceso denegado. Solo administradores pueden usar este comando.")
        return
    
    try:
        # Obtener estadísticas
        depositos_pendientes = await obtener_depositos_pendientes()
        retiros_pendientes = await obtener_retiros_pendientes()
        
        mensaje = (
            "🔧 Panel de Administración\n\n"
            f"📥 Depósitos pendientes: {len(depositos_pendientes)}\n"
            f"📤 Retiros pendientes: {len(retiros_pendientes)}\n\n"
            "Selecciona una opción:"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📥 Ver Depósitos", callback_data="admin_depositos")
        builder.button(text="📤 Ver Retiros", callback_data="admin_retiros")
        builder.button(text="📊 Estadísticas", callback_data="admin_stats")
        builder.adjust(2)
        keyboard = builder.as_markup()
        
        await message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error en panel admin: {e}")
        await message.answer("❌ Error cargando el panel de administración.")

async def admin_depositos_handler(callback: types.CallbackQuery):
    """Muestra lista de depósitos pendientes"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    
    try:
        depositos = await obtener_depositos_pendientes()
        
        if not depositos:
            await callback.message.edit_text(
                "📥 Depósitos Pendientes\n\n"
                "No hay depósitos pendientes de revisión.",
                parse_mode="HTML"
            )
            return
        
        mensaje = "📥 Depósitos Pendientes\n\n"
        for i, dep in enumerate(depositos[:10], 1):  # Mostrar máximo 10
            mensaje += (
                f"{i}. ID: {dep['_id']}\n"
                f"   Usuario: {dep['user_id']}\n"
                f"   Cantidad: {dep.get('cantidad', 'N/A')} {dep.get('network_name', 'TON')}\n"
                f"   Fecha: {dep['fecha'].strftime('%Y-%m-%d %H:%M')}\n\n"
            )
        
        if len(depositos) > 10:
            mensaje += f"... y {len(depositos) - 10} más\n\n"
        
        mensaje += "Las notificaciones llegarán automáticamente cuando se registren nuevos depósitos."
        
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_panel_volver")]
        ])
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        
    except Exception as e:
        logger.error(f"Error mostrando depósitos: {e}")
        await callback.answer("❌ Error cargando depósitos", show_alert=True)
    
    await callback.answer()

async def admin_retiros_handler(callback: types.CallbackQuery):
    """Muestra lista de retiros pendientes"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    
    try:
        retiros = await obtener_retiros_pendientes()
        
        if not retiros:
            await callback.message.edit_text(
                "📤 Retiros Pendientes\n\n"
                "No hay retiros pendientes de procesamiento.",
                parse_mode="HTML"
            )
            return
        
        mensaje = "📤 Retiros Pendientes\n\n"
        for i, ret in enumerate(retiros[:10], 1):  # Mostrar máximo 10
            mensaje += (
                f"{i}. ID: {ret['_id']}\n"
                f"   Usuario: {ret['user_id']}\n"
                f"   Cantidad: {ret.get('cantidad', 'N/A')} TON\n"
                f"   Wallet: {ret.get('wallet', 'N/A')}\n"
                f"   Fecha: {ret['fecha'].strftime('%Y-%m-%d %H:%M')}\n\n"
            )
        
        if len(retiros) > 10:
            mensaje += f"... y {len(retiros) - 10} más\n\n"
        
        mensaje += "Las notificaciones llegarán automáticamente cuando se registren nuevos retiros."
        
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_panel_volver")]
        ])
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        
    except Exception as e:
        logger.error(f"Error mostrando retiros: {e}")
        await callback.answer("❌ Error cargando retiros", show_alert=True)
    
    await callback.answer()

async def admin_stats_handler(callback: types.CallbackQuery):
    """Muestra estadísticas del sistema"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    
    try:
        from utils.database import obtener_estadisticas_generales, obtener_usuarios_activos
        
        stats = await obtener_estadisticas_generales()
        usuarios_activos = await obtener_usuarios_activos(7)
        
        mensaje = (
            "📊 Estadísticas del Sistema\n\n"
            f"👥 Total usuarios: {stats.get('total_usuarios', 0):,}\n"
            f"📥 Total depósitos: {stats.get('total_depositos', 0):,}\n"
            f"📤 Total retiros: {stats.get('total_retiros', 0):,}\n"
            f"💰 Volumen total: {stats.get('volumen_total', 0):.2f} TON\n"
            f"🟢 Usuarios activos (7d): {usuarios_activos:,}\n\n"
            "Última actualización: Ahora"
        )
        
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_panel_volver")]
        ])
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        
    except Exception as e:
        logger.error(f"Error mostrando estadísticas: {e}")
        await callback.answer("❌ Error cargando estadísticas", show_alert=True)
    
    await callback.answer()

async def admin_panel_volver_handler(callback: types.CallbackQuery):
    """Vuelve al panel principal de administración"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Acceso denegado", show_alert=True)
        return
    
    try:
        # Obtener estadísticas
        depositos_pendientes = await obtener_depositos_pendientes()
        retiros_pendientes = await obtener_retiros_pendientes()
        
        mensaje = (
            "🔧 Panel de Administración\n\n"
            f"📥 Depósitos pendientes: {len(depositos_pendientes)}\n"
            f"📤 Retiros pendientes: {len(retiros_pendientes)}\n\n"
            "Selecciona una opción:"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📥 Ver Depósitos", callback_data="admin_depositos")
        builder.button(text="📤 Ver Retiros", callback_data="admin_retiros")
        builder.button(text="📊 Estadísticas", callback_data="admin_stats")
        builder.adjust(2)
        keyboard = builder.as_markup()
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error en panel admin volver: {e}")
        await callback.answer("❌ Error cargando el panel de administración", show_alert=True)
    
    await callback.answer()

# =========================
# REGISTRO DE HANDLERS
# =========================

def register_admin_handlers(dp):
    """Registra todos los handlers de administración"""
    
    # Comandos de administración
    dp.message.register(admin_panel_handler, lambda m: m.text == "/admin")
    
    # Callbacks de notificaciones
    dp.callback_query.register(
        admin_deposito_notificacion_handler, 
        lambda c: c.data.startswith("admin_deposito_")
    )
    dp.callback_query.register(
        admin_retiro_notificacion_handler, 
        lambda c: c.data.startswith("admin_retiro_")
    )
    
    # Callbacks del panel de administración
    dp.callback_query.register(admin_depositos_handler, lambda c: c.data == "admin_depositos")
    dp.callback_query.register(admin_retiros_handler, lambda c: c.data == "admin_retiros")
    dp.callback_query.register(admin_stats_handler, lambda c: c.data == "admin_stats")
    dp.callback_query.register(admin_panel_volver_handler, lambda c: c.data == "admin_panel_volver")
    
    # Handlers de FSM para administración
    dp.message.register(procesar_cantidad_deposito_admin, AdminStates.esperando_cantidad_deposito) 