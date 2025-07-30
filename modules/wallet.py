from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import httpx
import datetime
import logging
from utils.database import (
    obtener_balance_usuario,
    creditos_col,
    descontar_balance_usuario,
    log_action,
    depositos_col,
)
from modules.constants import (
    REDES_SOPORTADAS,
    SISTEMA_CONFIG,
    MONEDA_PRINCIPAL
)

logger = logging.getLogger(__name__)

# Estados para la máquina de estados (FSM)
class WalletStates(StatesGroup):
    esperando_wallet = State()
    esperando_cantidad = State()
    esperando_cantidad_deposito = State()
    esperando_hash_deposito = State()

class WalletAddresses:
    """Clase para almacenar las direcciones de wallet de cada red"""

    def __init__(self):
        self.addresses = {
            "usdt_ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9",
            "usdt_trc20": "TQK5ReD72zeh8V2CnosrC6AjKRamt2PSwC",
            "ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9"
        }

    def get_address(self, network: str) -> str:
        return self.addresses.get(network, "Dirección no disponible")

    def get_all_addresses(self) -> dict:
        return self.addresses.copy()

wallet_addresses = WalletAddresses()

async def wallet_handler(event):
    """Handler principal del módulo wallet (funciona con mensajes y callbacks)"""
    # Determinar si es un mensaje o callback
    if hasattr(event, 'from_user'):
        user_id = event.from_user.id
        is_callback = hasattr(event, 'data')
    else:
        return
    
    balance_ton = await obtener_balance_usuario(user_id)
    
    mensaje = (
        "<b>👛 WALLET</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Gestiona tus fondos en Mundo Mítico.</b>\n\n"
        f"<b>💰 Balance:</b> <code>{balance_ton:.3f} TON</code>\n\n"
        "<b>Selecciona una opción para continuar:</b>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 Depositar", callback_data="wallet_depositar")
    builder.button(text="📤 Retirar", callback_data="wallet_retirar")
    builder.button(text="🔙 Volver", callback_data="perfil")
    builder.adjust(2)
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

async def wallet_depositar_handler(callback: types.CallbackQuery):
    """Handler para mostrar opciones de depósito"""
    mensaje = (
        "<b>📥 DEPÓSITO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Paso 1 de 2</b>\n\n"
        "<b>Redes disponibles:</b>\n"
        "  • 💎 USDT TON\n"
        "  • 💵 USDT TRC20\n"
        "  • 🪙 TON\n\n"
        "<b>Mínimo:</b> 0.5 TON (o equivalente en USD)\n\n"
        "Selecciona la red para obtener la dirección de depósito."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="USDT TON", callback_data="depositar_usdt_ton")
    builder.button(text="USDT TRC20", callback_data="depositar_usdt_trc20")
    builder.button(text="TON", callback_data="depositar_ton")
    builder.button(text="🔙 Volver", callback_data="perfil")
    builder.adjust(2, 1, 1)
    keyboard = builder.as_markup()
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

async def obtener_precios():
    """Obtiene precios actuales de TON y USDT desde CoinGecko"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "the-open-network,tether",
        "vs_currencies": "usd"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"CoinGecko API error: {response.status_code}")
                return None, None
            
            data = response.json()
            precio_ton = data.get("the-open-network", {}).get("usd")
            precio_usdt = data.get("tether", {}).get("usd")
            return precio_ton, precio_usdt
            
    except Exception as e:
        logger.error(f"Error al consultar CoinGecko: {e}")
        return None, None

async def handle_deposit_network(callback: types.CallbackQuery, state: FSMContext):
    """Handler para procesar la selección de red de depósito"""
    network_map = {
        "depositar_usdt_ton": ("USDT TON", "usdt_ton"),
        "depositar_usdt_trc20": ("USDT TRC20", "usdt_trc20"),
        "depositar_ton": ("TON", "ton")
    }
    
    callback_data = callback.data
    if callback_data not in network_map:
        await callback.answer("<b>❌ Red no válida.</b>", show_alert=True)
        return

    network_name, network_key = network_map[callback_data]
    address = wallet_addresses.get_address(network_key)
    
    # Obtener precios actuales
    precio_ton, precio_usdt = await obtener_precios()
    
    if precio_ton is None or precio_usdt is None:
        await callback.message.answer(
            "<b>❌ No se pudieron obtener los precios actuales.</b>\nIntenta de nuevo más tarde.",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Calcular mínimo equivalente
    min_ton = 0.5
    min_usdt = min_ton * precio_ton if precio_ton else "?"

    if network_key.startswith("usdt"):
        minimo = f"{min_usdt:.2f} USDT"
    else:
        minimo = f"{min_ton:.3f} TON"

    mensaje = (
        f"<b>📥 DEPÓSITO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Red seleccionada:</b> {network_name}\n"
        f"<b>Dirección:</b> <code>{address}</code>\n"
        f"<b>Mínimo:</b> {minimo}\n\n"
        "<b>Instrucciones:</b>\n"
        "1️⃣ Envía fondos a la dirección mostrada.\n"
        "2️⃣ Ingresa la cantidad exacta que enviaste.\n\n"
        "Puedes cancelar el proceso en cualquier momento."
    )
    
    await state.update_data(network_name=network_name, network_key=network_key, address=address)
    await state.set_state(WalletStates.esperando_cantidad_deposito)
    
    cancelar_keyboard = InlineKeyboardBuilder()
    cancelar_keyboard.button(text="❌ Cancelar", callback_data="cancelar_deposito")
    keyboard = cancelar_keyboard.as_markup()
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
    
    await callback.answer()

async def wallet_retirar_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handler para mostrar opciones de retiro"""
    user_id = callback.from_user.id
    balance_ton = await obtener_balance_usuario(user_id)
    min_retiro = 1.1

    if balance_ton == 0:
        mensaje = (
            "<b>❌ Retiro no disponible</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>💰 Balance:</b> <code>{balance_ton:.3f} TON</code>\n"
            f"<b>Mínimo de retiro:</b> <code>{min_retiro:.3f} TON</code>\n\n"
            "No tienes fondos disponibles para retirar.\n\n"
            "<b>Consejo:</b> Primero debes depositar fondos o comprar criaturas para generar ganancias."
        )
    elif balance_ton < min_retiro:
        mensaje = (
            "<b>❌ Retiro no disponible</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>💰 Balance:</b> <code>{balance_ton:.3f} TON</code>\n"
            f"<b>Mínimo de retiro:</b> <code>{min_retiro:.3f} TON</code>\n\n"
            "Tu balance es insuficiente para realizar un retiro.\n\n"
            "<b>Consejo:</b> Deposita más fondos o espera a que tus criaturas generen más ganancias."
        )
    else:
        mensaje = (
            "<b>📤 RETIRO</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Paso 1 de 2</b>\n\n"
            f"<b>💰 Balance:</b> <code>{balance_ton:.3f} TON</code>\n"
            f"<b>Mínimo de retiro:</b> <code>{min_retiro:.3f} TON</code>\n\n"
            "<b>Instrucciones:</b>\n"
            "1️⃣ Envía tu dirección de wallet TON.\n"
            "2️⃣ Ingresa la cantidad a retirar.\n\n"
            "Puedes cancelar el proceso en cualquier momento."
        )
        await state.update_data(balance=balance_ton, min_retiro=min_retiro)
        await state.set_state(WalletStates.esperando_wallet)
    
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="wallet")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="perfil")]
    ])
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    await callback.answer()

async def procesar_wallet_ton(message: types.Message, state: FSMContext):
    """Procesa la dirección de wallet TON ingresada"""
    user_id = message.from_user.id
    wallet_address = message.text.strip()
    current_state = await state.get_state()
    
    if current_state != WalletStates.esperando_wallet.state:
        await message.answer(
            "<b>Comando no disponible</b>\n\nPara agregar tu wallet TON, ve a <b>Wallet → Retirar</b>.",
            parse_mode="HTML"
        )
        return

    if not wallet_address.startswith("UQ") or len(wallet_address) < 48:
        await message.answer(
            "<b>❌ Dirección inválida</b>\n\nLa dirección de wallet TON debe comenzar con 'UQ' y tener al menos 48 caracteres.\nAsegúrate de copiar la dirección completa de tu wallet TON.",
            parse_mode="HTML"
        )
        return

    await state.update_data(wallet_address=wallet_address)
    await state.set_state(WalletStates.esperando_cantidad)
    
    data = await state.get_data()
    balance = data.get('balance', 0)
    min_retiro = data.get('min_retiro', 1.1)
    
    mensaje = (
        "<b>📤 RETIRO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Paso 2 de 2</b>\n\n"
        f"<b>Wallet TON registrada:</b> <code>{wallet_address}</code>\n"
        f"<b>💰 Balance disponible:</b> <code>{balance:.3f} TON</code>\n"
        f"<b>Mínimo de retiro:</b> <code>{min_retiro:.3f} TON</code>\n\n"
        "Ahora ingresa la cantidad que deseas retirar (en TON).\n\n"
        "Puedes cancelar el proceso en cualquier momento."
    )
    
    cancelar_keyboard = InlineKeyboardBuilder()
    cancelar_keyboard.button(text="❌ Cancelar", callback_data="cancelar_retiro_total")
    keyboard = cancelar_keyboard.as_markup()
    
    await message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def procesar_cantidad_retiro(message: types.Message, state: FSMContext):
    """Procesa la cantidad de retiro ingresada"""
    user_id = message.from_user.id
    cantidad_text = message.text.strip().replace(",", ".")
    current_state = await state.get_state()
    
    if current_state != WalletStates.esperando_cantidad.state:
        return

    try:
        cantidad = float(cantidad_text)
        if cantidad <= 0:
            raise ValueError
    except Exception:
        await message.answer(
            "<b>❌ Cantidad inválida</b>\n\nPor favor, ingresa un número válido mayor a 0.",
            parse_mode="HTML"
        )
        return

    balance = await obtener_balance_usuario(user_id)
    data = await state.get_data()
    min_retiro = data.get('min_retiro', 1.1)
    wallet_address = data.get('wallet_address', '')

    if cantidad < min_retiro:
        await message.answer(
            f"<b>❌ Cantidad insuficiente</b>\n\nLa cantidad mínima de retiro es <code>{min_retiro:.3f} TON</code>.\nTu solicitud: <code>{cantidad:.3f} TON</code>",
            parse_mode="HTML"
        )
        return

    if cantidad > balance:
        await message.answer(
            f"<b>❌ Balance insuficiente</b>\n\nTu balance disponible es <code>{balance:.3f} TON</code>.\nTu solicitud: <code>{cantidad:.3f} TON</code>",
            parse_mode="HTML"
        )
        return

    await state.update_data(cantidad=cantidad)
    
    mensaje = (
        "<b>📤 CONFIRMAR RETIRO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Cantidad:</b> <code>{cantidad:.3f} TON</code>\n"
        f"<b>Wallet:</b> <code>{wallet_address}</code>\n\n"
        "¿Deseas confirmar este retiro?\n\n"
        "<b>⏳ Tiempo estimado:</b> 24-48 horas\n\n"
        "Puedes cancelar el proceso si lo deseas."
    )
    
    confirm_keyboard = InlineKeyboardBuilder()
    confirm_keyboard.button(text="✅ Confirmar", callback_data="confirmar_retiro")
    confirm_keyboard.button(text="❌ Cancelar", callback_data="cancelar_retiro_total")
    keyboard = confirm_keyboard.as_markup()
    
    await message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def confirmar_retiro_handler(callback: types.CallbackQuery, state: FSMContext):
    """Confirma y procesa el retiro"""
    user_id = callback.from_user.id
    data = await state.get_data()
    cantidad = data.get('cantidad')
    wallet_address = data.get('wallet_address')

    if not cantidad or not wallet_address:
        await callback.answer("<b>❌ Datos incompletos para el retiro.</b>", show_alert=True)
        return

    ok = await descontar_balance_usuario(user_id, cantidad)
    if not ok:
        await callback.answer("<b>❌ Balance insuficiente para procesar el retiro.</b>", show_alert=True)
        return

    retiro_data = {
        "user_id": user_id,
        "tipo": "retiro",
        "estado": "pendiente",
        "cantidad": cantidad,
        "wallet": wallet_address,
        "fecha": datetime.datetime.now()
    }
    
    result = await creditos_col.insert_one(retiro_data)
    retiro_id = str(result.inserted_id)
    
    await log_action(user_id, "retiro_solicitado", details={
        "cantidad": cantidad, 
        "wallet": wallet_address,
        "retiro_id": retiro_id
    })

    mensaje = (
        "<b>📤 RETIRO SOLICITADO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>ID de Retiro:</b> <code>{retiro_id}</code>\n"
        f"<b>Cantidad:</b> <code>{cantidad:.3f} TON</code>\n"
        f"<b>Wallet:</b> <code>{wallet_address}</code>\n\n"
        "Tu solicitud está pendiente de revisión.\n\n"
        "<b>⏳ Tiempo estimado:</b> 24-48 horas\n\n"
        "Guarda este ID para cualquier reporte o consulta."
    )
    
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="wallet")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
    ])
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    
    await state.clear()
    await callback.answer()

async def procesar_cantidad_deposito(message: types.Message, state: FSMContext):
    """Procesa la cantidad de depósito ingresada"""
    current_state = await state.get_state()
    if current_state != WalletStates.esperando_cantidad_deposito.state:
        return
    
    user_id = message.from_user.id
    cantidad_text = message.text.strip().replace(",", ".")
    
    try:
        cantidad = float(cantidad_text)
        if cantidad <= 0:
            raise ValueError
    except Exception:
        await message.answer(
            "<b>❌ Cantidad inválida</b>\n\nPor favor, ingresa un número válido mayor a 0.",
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    network_key = data.get('network_key', 'ton')
    network_name = data.get('network_name', 'desconocida')
    address = data.get('address', '')
    
    precio_ton, precio_usdt = await obtener_precios()
    equivalente_ton = cantidad
    
    if network_key.startswith("usdt"):
        if precio_ton and precio_usdt:
            equivalente_ton = cantidad * (precio_usdt / precio_ton)
    
    await state.update_data(cantidad=cantidad, equivalente_ton=equivalente_ton)
    await state.set_state(WalletStates.esperando_hash_deposito)
    
    resumen = (
        "<b>📥 DEPÓSITO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Red:</b> {network_name}\n"
        f"<b>Dirección:</b> <code>{address}</code>\n"
        f"<b>Cantidad enviada:</b> <code>{cantidad:.3f} {network_name.split()[-1]}</code>\n"
        f"<b>Equivalente estimado:</b> <code>{equivalente_ton:.3f} TON</code>\n\n"
        "Ahora responde a este mensaje con el hash de tu transacción para acreditar tu depósito.\n\n"
        "Si deseas cancelar el proceso, pulsa el botón abajo."
    )
    
    cancelar_keyboard = InlineKeyboardBuilder()
    cancelar_keyboard.button(text="❌ Cancelar", callback_data="cancelar_deposito")
    keyboard = cancelar_keyboard.as_markup()
    
    try:
        await message.edit_text(resumen, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await message.answer(resumen, parse_mode="HTML", reply_markup=keyboard)

async def procesar_hash_deposito(message: types.Message, state: FSMContext):
    """Procesa el hash de depósito ingresado"""
    current_state = await state.get_state()
    if current_state != WalletStates.esperando_hash_deposito.state:
        return
    
    user_id = message.from_user.id
    hash_text = message.text.strip()
    data = await state.get_data()
    
    network_name = data.get('network_name', 'desconocida')
    network_key = data.get('network_key', 'desconocida')
    address = data.get('address', '')
    cantidad = data.get('cantidad', None)
    
    if cantidad is None:
        await message.answer(
            "<b>❌ Error</b>\n\n<i>Primero debes ingresar la cantidad a depositar antes de enviar el hash.</i>",
            parse_mode="HTML"
        )
        return
    
    deposito_data = {
        "user_id": user_id,
        "hash": hash_text,
        "network_key": network_key,
        "network_name": network_name,
        "address": address,
        "cantidad": cantidad,
        "estado": "pendiente",
        "fecha": datetime.datetime.now()
    }
    
    result = await depositos_col.insert_one(deposito_data)
    deposito_id = str(result.inserted_id)
    
    await log_action(user_id, "deposito_registrado", details={
        "network": network_name,
        "cantidad": cantidad,
        "hash": hash_text,
        "deposito_id": deposito_id
    })
    
    mensaje_confirmacion = (
        "<b>📥 DEPÓSITO REGISTRADO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>ID de Depósito:</b> <code>{deposito_id}</code>\n"
        f"<b>Red:</b> {network_name}\n"
        f"<b>Dirección:</b> <code>{address}</code>\n"
        f"<b>Cantidad:</b> <code>{cantidad:.3f}</code> {network_name.split()[-1]}\n"
        f"<b>Hash:</b>\n<code>{hash_text}</code>\n\n"
        "<b>Estado:</b> <b>Pendiente de revisión</b>\n"
        "<b>⏳ Tiempo estimado:</b> 24-48 horas\n\n"
        "Guarda este ID para cualquier reporte o consulta."
    )
    
    await message.answer(mensaje_confirmacion, parse_mode="HTML")
    
    await state.clear()

async def cancelar_deposito_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancela el proceso de depósito"""
    await state.clear()
    mensaje = (
        "<b>❌ Depósito cancelado</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "El proceso de depósito ha sido cancelado. Puedes iniciar uno nuevo desde <b>Wallet → Depositar</b>."
    )
    
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="wallet")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
    ])
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    await callback.answer()

async def cancelar_retiro_handler(callback: types.CallbackQuery):
    """Cancela el proceso de retiro"""
    mensaje = (
        "<b>❌ Retiro cancelado</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Tu solicitud de retiro ha sido cancelada.\nPuedes iniciar un nuevo retiro desde <b>Wallet → Retirar</b>."
    )
    
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="wallet_volver")]
    ])
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    await callback.answer()

async def cancelar_retiro_total_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancela completamente el proceso de retiro"""
    await state.clear()
    mensaje = (
        "<b>❌ Retiro cancelado</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "El proceso de retiro ha sido cancelado. Puedes iniciar uno nuevo desde <b>Wallet → Retirar</b>."
    )
    
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="wallet")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="perfil")]
    ])
    
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    await callback.answer()


def register_wallet_handlers(dp):
    """Registra todos los handlers del módulo wallet"""
    dp.callback_query.register(wallet_depositar_handler, lambda c: c.data == "wallet_depositar")
    dp.callback_query.register(wallet_retirar_handler, lambda c: c.data == "wallet_retirar")
    dp.callback_query.register(handle_deposit_network, lambda c: c.data.startswith("depositar_"))

    dp.callback_query.register(confirmar_retiro_handler, lambda c: c.data == "confirmar_retiro")
    dp.callback_query.register(cancelar_retiro_handler, lambda c: c.data == "cancelar_retiro")
    dp.callback_query.register(cancelar_deposito_handler, lambda c: c.data == "cancelar_deposito")
    dp.callback_query.register(cancelar_retiro_total_handler, lambda c: c.data == "cancelar_retiro_total")

    dp.message.register(procesar_wallet_ton, WalletStates.esperando_wallet)
    dp.message.register(procesar_cantidad_retiro, WalletStates.esperando_cantidad)
    dp.message.register(procesar_cantidad_deposito, WalletStates.esperando_cantidad_deposito)
    dp.message.register(procesar_hash_deposito, WalletStates.esperando_hash_deposito)
    
