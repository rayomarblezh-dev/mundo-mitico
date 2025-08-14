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
        "<b>Wallet</b>\n\n"
        f"Balance: {balance_ton:.3f} TON\n\n"
        "<b>Manage your funds in Mundo Mágico.</b>\n\n"
        "<b>Select an option to continue:</b>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Deposit", callback_data="wallet_depositar")
    builder.button(text="Withdraw", callback_data="wallet_retirar")
    builder.button(text="« Back to Profile" , callback_data="perfil")
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
        "<b>Deposit</b>\n\n"
        "<b>Step 1 of 2</b>\n\n"
        "<b>Available networks:</b>\n"
        "  • USDT TON\n"
        "  • USDT TRC20\n"
        "  • TON\n\n"
        "<b>Minimum:</b> 0.5 TON (or equivalent in USD)\n\n"
        "Select the network to get the deposit address."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="USDT TON", callback_data="depositar_usdt_ton")
    builder.button(text="USDT TRC20", callback_data="depositar_usdt_trc20")
    builder.button(text="TON", callback_data="depositar_ton")
    builder.button(text="« Back to Wallet", callback_data="wallet")
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
        await callback.answer("❌ Invalid network.", show_alert=True)
        return

    network_name, network_key = network_map[callback_data]
    address = wallet_addresses.get_address(network_key)
    
    # Obtener precios actuales
    precio_ton, precio_usdt = await obtener_precios()
    
    if precio_ton is None or precio_usdt is None:
        await callback.answer(
            "❌ Could not get current prices. Try again later.",
            show_alert=True
        )
        return

    # Calcular mínimo equivalente
    min_ton = 0.5
    min_usdt = min_ton * precio_ton if precio_ton else "?"

    if network_key.startswith("usdt"):
        minimo = f"{min_usdt:.2f} USDT"
    else:
        minimo = f"{min_ton:.3f} TON"

    mensaje = (
        f"<b>Deposit</b>\n\n"
        f"<b>Network:</b> {network_name}\n"
        f"<b>Address:</b> <code>{address}</code>\n"
        f"<b>Minimum:</b> {minimo}\n\n"
        "<b>Instructions:</b>\n"
        "1. Send funds to the address shown.\n"
        "2. Enter the exact amount you sent.\n\n"
        "You can cancel the process at any time."
    )
    
    await state.update_data(network_name=network_name, network_key=network_key, address=address)
    await state.set_state(WalletStates.esperando_cantidad_deposito)
    
    cancelar_keyboard = InlineKeyboardBuilder()
    cancelar_keyboard.button(text="« Back to Wallet", callback_data="wallet")
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
        await callback.answer(
            "❌ Withdrawal not available", show_alert=True
        )
        return
    elif balance_ton < min_retiro:
        await callback.answer(
            "❌ Withdrawal not available", show_alert=True
        )
        return

    mensaje = (
        "<b>Withdraw</b>\n\n"
        "<b>Step 1 of 2</b>\n\n"
        f"<b>Balance:</b> <code>{balance_ton:.3f} TON</code>\n"
        f"<b>Minimum withdrawal:</b> <code>{min_retiro:.3f} TON</code>\n\n"
        "<b>Instructions:</b>\n"
        "1. Send your TON wallet address.\n"
        "2. Enter the amount to withdraw.\n\n"
        "You can cancel the process at any time."
    )
    await state.update_data(balance=balance_ton, min_retiro=min_retiro)
    await state.set_state(WalletStates.esperando_wallet)
    
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Wallet", callback_data="wallet")],
    ])
    
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    except Exception as e:
        if "message is not modified" in str(e):
            pass
        else:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
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
            "<b>❌ Invalid amount</b>\n\nPlease enter a valid number greater than 0.",
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    network_name = data.get('network_name', '')
    address = data.get('address', '')
    
    mensaje = (
        "<b>Deposit</b>\n"
        "<b>Step 2 of 2</b>\n\n"
        f"<b>Network:</b> {network_name}\n"
        f"<b>Address:</b> <code>{address}</code>\n"
        f"<b>Amount:</b> <code>{cantidad:.3f} {network_name}</code>\n\n"
        "Do you want to confirm the deposit?\n\n"
        "You can cancel the process at any time."
    )
    
    confirm_keyboard = InlineKeyboardBuilder()
    confirm_keyboard.button(text="✅", callback_data="confirmar_deposito")
    confirm_keyboard.button(text="❌", callback_data="wallet")
    keyboard = confirm_keyboard.as_markup()
    
    await message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def confirmar_deposito_handler(callback: types.CallbackQuery, state: FSMContext):
    """Confirma y procesa el depósito"""
    user_id = callback.from_user.id
    data = await state.get_data()
    cantidad = data.get('cantidad')
    network_name = data.get('network_name')
    address = data.get('address')

    if not cantidad or not network_name or not address:
        await callback.answer("<b>❌ Invalid data for deposit.</b>", show_alert=True)
        return
    
    ok = await add_balance_usuario(user_id, cantidad, network_name)
    if not ok:
        await callback.answer("<b>❌ Balance not updated.</b>", show_alert=True)
        return

    deposit_data = {
        "user_id": user_id,
        "tipo": "deposito",
        "estado": "pendiente",
        "cantidad": cantidad,
        "network": network_name,
        "address": address,
        "fecha": datetime.datetime.now()
    }
    
    result = await creditos_col.insert_one(deposit_data)
    deposit_id = str(result.inserted_id)
    
    await log_action(user_id, "deposito_solicitado", details={
        "cantidad": cantidad, 
        "network": network_name,
        "address": address,
        "deposit_id": deposit_id
    })

    mensaje = (
        "<b>Deposit</b>\n"
        f"<b>Amount:</b> <code>{cantidad:.3f} {network_name}</code>\n"
        f"<b>Address:</b> <code>{address}</code>\n\n"
        "Your deposit request is pending review.\n\n"
    )
    
    volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Wallet", callback_data="wallet")],
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
            "<b>Invalid amount</b>\n\nPlease enter a valid number greater than 0.",
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    network_key = data.get('network_key', 'ton')
    network_name = data.get('network_name', 'unknown')
    address = data.get('address', '')
    
    precio_ton, precio_usdt = await obtener_precios()
    equivalente_ton = cantidad
    
    if network_key.startswith("usdt"):
        if precio_ton and precio_usdt:
            equivalente_ton = cantidad * (precio_usdt / precio_ton)
    
    await state.update_data(cantidad=cantidad, equivalente_ton=equivalente_ton)
    await state.set_state(WalletStates.esperando_hash_deposito)
    
    resumen = (
        "<b>Deposit</b>\n"
        f"<b>Network:</b> {network_name}\n"
        f"<b>Address:</b>\n <blockquote><code>{address}</code></blockquote>\n"
        f"<b>Amount:</b> <code>{cantidad:.3f} {network_name.split()[-1]}</code>\n"
        f"<b>Equivalent:</b> <code>{equivalente_ton:.3f} TON</code>\n\n"
        "Now respond to this message with your transaction hash.\n\n"
        "If you want to cancel the process, press the button below."
    )
    
    cancelar_keyboard = InlineKeyboardBuilder()
    cancelar_keyboard.button(text="« Back to Wallet", callback_data="wallet")
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
    
    network_name = data.get('network_name', 'unknown')
    network_key = data.get('network_key', 'unknown')
    address = data.get('address', '')
    cantidad = data.get('cantidad', None)
    
    if cantidad is None:
        await message.answer(
            "<b>Error</b>\n\n<i>You must enter the deposit amount before sending the hash.</i>",
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
        "<b>Deposit</b>\n"
        f"<b>Network:</b> {network_name}\n"
        f"<b>Address:</b> <code>{address}</code>\n"
        f"<b>Amount:</b> <code>{cantidad:.3f}</code> {network_name.split()[-1]}\n"
        f"<b>Hash:</b>\n<code>{hash_text}</code>\n\n"
        "<b>Status:</b> <b>Pending</b>\n"
    )
    
    await message.answer(mensaje_confirmacion, parse_mode="HTML")
    
    await state.clear()

async def confirmar_retiro_handler(callback: types.CallbackQuery, state: FSMContext):
    """Confirma y procesa el retiro"""
    try:
        data = await state.get_data()
        user_id = callback.from_user.id
        cantidad = data.get('cantidad')
        wallet = data.get('wallet')
        moneda = data.get('moneda', 'TON')
        
        # Aquí iría la lógica para procesar el retiro
        # Por ejemplo, verificar fondos, registrar la transacción, etc.
        
        await callback.message.edit_text(
            f"Withdrawal of {cantidad} {moneda} processed successfully.\n"
            f"Sending to: {wallet}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="« Back to Wallet", callback_data="wallet")]
            ])
        )
        
        # Limpiar el estado
        await state.clear()
        
    except Exception as e:
        logging.error(f"Error in confirmar_retiro_handler: {str(e)}")
        await callback.message.edit_text(
            "❌ An error occurred while processing the withdrawal. Please try again.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="« Back to Wallet", callback_data="wallet")]
            ])
        )
        await state.clear()

async def wallet_back_handler(callback: types.CallbackQuery, state: FSMContext):
    """Maneja el botón de volver al menú de wallet con limpieza de FSM"""
    await state.clear()
    await wallet_handler(callback)

async def wallet_back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Vuelve al menú principal con limpieza de FSM"""
    await state.clear()
    from modules.start import start_handler
    await start_handler(callback)

def register_wallet_handlers(dp):
    """Registra todos los handlers del módulo wallet"""
    dp.callback_query.register(wallet_depositar_handler, lambda c: c.data == "wallet_depositar")
    dp.callback_query.register(wallet_retirar_handler, lambda c: c.data == "wallet_retirar")

    # Register state handlers
    dp.message.register(procesar_cantidad_deposito, WalletStates.esperando_cantidad_deposito)
    dp.message.register(procesar_hash_deposito, WalletStates.esperando_hash_deposito)
    
    # Register the withdrawal confirmation handler
    dp.callback_query.register(confirmar_retiro_handler, lambda c: c.data == "confirmar_retiro")
    
    # Register cancel handlers that use the back handler
    dp.callback_query.register(wallet_back_handler, lambda c: c.data in [
        "wallet"  # Handle direct wallet callback
    ])
