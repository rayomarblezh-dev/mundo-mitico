from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import httpx
import datetime
import bson
from utils.database import (
    obtener_balance_usuario,
    creditos_col,
    descontar_balance_usuario,
    log_action,
    notificar_admins_nuevo_deposito,
    notificar_admins_nuevo_retiro,
    depositos_col,
)
from modules.constants import EMOJI_DEPOSITO, EMOJI_RETIRO

# Estados para la máquina de estados (FSM)
class WalletStates(StatesGroup):
    esperando_wallet = State()
    esperando_cantidad = State()
    esperando_cantidad_deposito = State()
    esperando_hash_deposito = State()

# Diccionario para controlar usuarios que están agregando wallet (no usado, pero mantenido por compatibilidad)
usuarios_agregando_wallet = {}

class WalletAddresses:
    """Clase para almacenar las direcciones de wallet de cada red"""

    def __init__(self):
        self.addresses = {
            "usdt_bep20": "0xca1BEE70DA9c00b7cB61AA145F3BEFFbCAe4CC0F",
            "usdt_ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9",
            "ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9",
            "trx_trc20": "TGhQFGDDhKJE79rQTgZ2QS5LP4KnoLQkc6"
        }

    def get_address(self, network: str) -> str:
        return self.addresses.get(network, "Dirección no disponible")

    def get_all_addresses(self) -> dict:
        return self.addresses.copy()

wallet_addresses = WalletAddresses()

async def wallet_handler(message: types.Message):
    user_id = message.from_user.id
    balance_ton = await obtener_balance_usuario(user_id)
    mensaje = (
        "<b>👛 Wallet</b>\n\n"
        "Gestiona tus fondos en <b>Mundo Mítico</b>.\n\n"
        f"<b>Balance:</b> <code>{balance_ton:.3f}</code> TON\n\n"
        "Selecciona una opción para continuar:"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{EMOJI_DEPOSITO} Depositar", callback_data="wallet_depositar")
    builder.button(text=f"{EMOJI_RETIRO} Retirar", callback_data="wallet_retirar")
    builder.adjust(2)
    keyboard = builder.as_markup()
    try:
        await message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def wallet_depositar_handler(callback: types.CallbackQuery):
    mensaje = (
        "<b>📥 Depósito - Paso 1 de 2</b>\n\n"
        "<b>Redes disponibles:</b>\n"
        "• USDT BEP20\n"
        "• USDT TON\n"
        "• TON\n"
        "• TRX TRC20\n\n"
        "<b>⚠️ Mínimo:</b> <code>0.5 TON</code> (o equivalente en USD)\n\n"
        "Selecciona la red para obtener la dirección de depósito."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="USDT BEP20", callback_data="depositar_usdt_bep20")
    builder.button(text="USDT TON", callback_data="depositar_usdt_ton")
    builder.button(text="TON", callback_data="depositar_ton")
    builder.button(text="TRX TRC20", callback_data="depositar_trx")
    builder.adjust(2)
    keyboard = builder.as_markup()
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

async def obtener_precios():
    import logging
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "the-open-network,tether,tron",
        "vs_currencies": "usd"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logging.warning(f"CoinGecko API error: {response.status_code} {response.text}")
                return None, None, None
            data = response.json()
            precio_ton = data.get("the-open-network", {}).get("usd")
            precio_usdt = data.get("tether", {}).get("usd")
            precio_trx = data.get("tron", {}).get("usd")
            return precio_ton, precio_usdt, precio_trx
    except Exception as e:
        logging.error(f"Error al consultar CoinGecko: {e}")
        return None, None, None

async def handle_deposit_network(callback: types.CallbackQuery, state: FSMContext):
    network_map = {
        "depositar_usdt_bep20": ("USDT BEP20", "usdt_bep20"),
        "depositar_usdt_ton": ("USDT TON", "usdt_ton"),
        "depositar_ton": ("TON", "ton"),
        "depositar_trx": ("TRX TRC20", "trx_trc20")
    }
    callback_data = callback.data
    if callback_data not in network_map:
        await callback.answer("Red no válida")
        return

    network_name, network_key = network_map[callback_data]
    address = wallet_addresses.get_address(network_key)
    precio_ton, precio_usdt, precio_trx = await obtener_precios()
    if precio_ton is None or precio_usdt is None or precio_trx is None:
        await callback.message.answer(
            "<b>⚠️ No se pudieron obtener los precios actuales de CoinGecko.</b>\nIntenta de nuevo más tarde.",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    min_ton = 0.5
    min_usdt = min_ton * precio_ton if precio_ton else "?"
    min_trx = min_usdt / precio_trx if precio_trx else "?"

    if network_key.startswith("usdt"):
        minimo = f"{min_usdt:.2f} USDT"
    elif network_key == "trx_trc20":
        minimo = f"{min_trx:.2f} TRX"
    else:
        minimo = f"{min_ton:.3f} TON"

    mensaje = (
        f"<b>📥 Depósito - Paso 1 de 2</b>\n\n"
        f"<b>Red seleccionada:</b> {network_name}\n"
        f"<b>Dirección:</b> <code>{address}</code>\n"
        f"<b>⚠️ Mínimo:</b> <code>{minimo}</code>\n\n"
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
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def wallet_retirar_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    balance_ton = await obtener_balance_usuario(user_id)
    min_retiro = 1.1

    if balance_ton == 0:
        mensaje = (
            "<b>❌ Retiro no disponible</b>\n\n"
            f"<b>💰 Balance:</b> <code>{balance_ton:.3f}</code> TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> <code>{min_retiro:.3f}</code> TON\n\n"
            "No tienes fondos disponibles para retirar.\n\n"
            "<b>💡 Consejo:</b> Primero debes depositar fondos o comprar criaturas para generar ganancias."
        )
    elif balance_ton < min_retiro:
        mensaje = (
            "<b>❌ Retiro no disponible</b>\n\n"
            f"<b>💰 Balance:</b> <code>{balance_ton:.3f}</code> TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> <code>{min_retiro:.3f}</code> TON\n\n"
            "Tu balance es insuficiente para realizar un retiro.\n\n"
            "<b>💡 Consejo:</b> Deposita más fondos o espera a que tus criaturas generen más ganancias."
        )
    else:
        mensaje = (
            "<b>📤 Retiro - Paso 1 de 2</b>\n\n"
            f"<b>Balance:</b> <code>{balance_ton:.3f}</code> TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> <code>{min_retiro:.3f}</code> TON\n\n"
            "<b>Instrucciones:</b>\n"
            "1️⃣ Envía tu dirección de wallet TON.\n"
            "2️⃣ Ingresa la cantidad a retirar.\n\n"
            "Puedes cancelar el proceso en cualquier momento."
        )
        await state.update_data(balance=balance_ton, min_retiro=min_retiro)
        await state.set_state(WalletStates.esperando_wallet)
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def procesar_cantidad_retiro(message: types.Message, state: FSMContext):
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
            "<b>❌ Cantidad inválida</b>\n\n<i>Por favor, ingresa un número válido mayor a 0.</i>",
            parse_mode="HTML"
        )
        return

    balance = await obtener_balance_usuario(user_id)
    data = await state.get_data()
    min_retiro = data.get('min_retiro', 1.1)
    wallet_address = data.get('wallet_address', '')

    if cantidad < min_retiro:
        await message.answer(
            f"<b>❌ Cantidad insuficiente</b>\n\n"
            f"La cantidad mínima de retiro es <b>{min_retiro:.3f} TON</b>.\n"
            f"Tu solicitud: <b>{cantidad:.3f} TON</b>",
            parse_mode="HTML"
        )
        return

    if cantidad > balance:
        await message.answer(
            f"<b>❌ Balance insuficiente</b>\n\n"
            f"Tu balance disponible es <b>{balance:.3f} TON</b>.\n"
            f"Tu solicitud: <b>{cantidad:.3f} TON</b>",
            parse_mode="HTML"
        )
        return

    await state.update_data(cantidad=cantidad)
    mensaje = (
        "<b>📤 Confirmar Retiro</b>\n\n"
        f"<b>💰 Cantidad:</b> <code>{cantidad:.3f}</code> TON\n"
        f"<b>Wallet:</b> <code>{wallet_address}</code>\n\n"
        "¿Deseas confirmar este retiro?\n\n"
        "<b>⏰ Tiempo estimado:</b> 24-48 horas\n\n"
        "Puedes cancelar el proceso si lo deseas."
    )
    confirm_keyboard = InlineKeyboardBuilder()
    confirm_keyboard.button(text="✅ Confirmar", callback_data="confirmar_retiro")
    confirm_keyboard.button(text="❌ Cancelar", callback_data="cancelar_retiro_total")
    keyboard = confirm_keyboard.as_markup()
    try:
        await message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def procesar_wallet_ton(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    wallet_address = message.text.strip()
    current_state = await state.get_state()
    if current_state != WalletStates.esperando_wallet.state:
        await message.answer(
            "<b>❌ Comando no disponible</b>\n\n"
            "Para agregar tu wallet TON, ve a <b>Wallet → Retirar</b>.",
            parse_mode="HTML"
        )
        return

    if not wallet_address.startswith("UQ") or len(wallet_address) < 48:
        await message.answer(
            "<b>❌ Dirección inválida</b>\n\n"
            "La dirección de wallet TON debe comenzar con 'UQ' y tener al menos 48 caracteres.\n"
            "Asegúrate de copiar la dirección completa de tu wallet TON.",
            parse_mode="HTML"
        )
        return

    await state.update_data(wallet_address=wallet_address)
    await state.set_state(WalletStates.esperando_cantidad)
    data = await state.get_data()
    balance = data.get('balance', 0)
    min_retiro = data.get('min_retiro', 1.1)
    mensaje = (
        "<b>📤 Retiro - Paso 2 de 2</b>\n\n"
        f"<b>Wallet TON registrada:</b> <code>{wallet_address}</code>\n"
        f"<b>💰 Balance disponible:</b> <code>{balance:.3f}</code> TON\n"
        f"<b>⚠️ Mínimo de retiro:</b> <code>{min_retiro:.3f}</code> TON\n\n"
        "Ahora ingresa la cantidad que deseas retirar (en TON).\n\n"
        "Puedes cancelar el proceso en cualquier momento."
    )
    cancelar_keyboard = InlineKeyboardBuilder()
    cancelar_keyboard.button(text="❌ Cancelar", callback_data="cancelar_retiro_total")
    keyboard = cancelar_keyboard.as_markup()
    try:
        await message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)

async def confirmar_retiro_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    cantidad = data.get('cantidad')
    wallet_address = data.get('wallet_address')

    if not cantidad or not wallet_address:
        await callback.answer("❌ Datos incompletos para el retiro.", show_alert=True)
        return

    ok = await descontar_balance_usuario(user_id, cantidad)
    if not ok:
        await callback.answer("❌ Balance insuficiente para procesar el retiro.", show_alert=True)
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
    await notificar_admins_nuevo_retiro(user_id, cantidad, wallet_address, retiro_id)
    await log_action(user_id, "retiro_solicitado", details={"cantidad": cantidad, "wallet": wallet_address})

    mensaje = (
        "<b>✅ Retiro solicitado</b>\n\n"
        f"<b>ID de Retiro:</b> <code>{retiro_id}</code>\n"
        f"<b>Cantidad:</b> <code>{cantidad:.3f}</code> TON\n"
        f"<b>Wallet:</b> <code>{wallet_address}</code>\n\n"
        "Tu solicitud está pendiente de revisión.\n\n"
        "<b>⏰ Tiempo estimado:</b> 24-48 horas\n"
        "<b>📧 Notificación:</b> Recibirás confirmación cuando se complete.\n\n"
        "Guarda este ID para cualquier reporte o consulta.\n"
        "Puedes consultar el estado con: <code>/estado [id]</code>"
    )
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await state.clear()
    await callback.answer()

async def cancelar_retiro_handler(callback: types.CallbackQuery):
    mensaje = (
        "<b>❌ Retiro cancelado</b>\n\n"
        "<i>Tu solicitud de retiro ha sido cancelada.\n"
        "Puedes iniciar un nuevo retiro desde Wallet → Retirar.</i>"
    )
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def procesar_cantidad_deposito(message: types.Message, state: FSMContext):
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
            "<b>❌ Cantidad inválida</b>\n\n<i>Por favor, ingresa un número válido mayor a 0.</i>",
            parse_mode="HTML"
        )
        return
    data = await state.get_data()
    network_key = data.get('network_key', 'ton')
    precio_ton, precio_usdt, precio_trx = await obtener_precios()
    equivalente_ton = cantidad
    if network_key in ("usdt_bep20", "usdt_ton"):
        if precio_ton and precio_usdt:
            equivalente_ton = cantidad * (precio_usdt / precio_ton)
    elif network_key == "trx_trc20":
        if precio_ton and precio_trx:
            equivalente_ton = cantidad * (precio_trx / precio_ton)
    await state.update_data(cantidad=cantidad, equivalente_ton=equivalente_ton)
    await state.set_state(WalletStates.esperando_hash_deposito)
    network_name = data.get('network_name', 'desconocida')
    address = data.get('address', '')
    resumen = (
        "<b>📥 Depósito - Paso 2 de 2</b>\n\n"
        f"<b>Red:</b> {network_name}\n"
        f"<b>Dirección:</b> <code>{address}</code>\n"
        f"<b>Cantidad enviada:</b> <code>{cantidad:.3f}</code> {network_name.split()[-1]}\n"
        f"<b>Equivalente estimado:</b> <code>{equivalente_ton:.3f}</code> TON\n\n"
        "Ahora responde a este mensaje con el <b>hash</b> de tu transacción para acreditar tu depósito.\n\n"
        "Si deseas cancelar el proceso, pulsa el botón abajo."
    )
    cancelar_keyboard = InlineKeyboardBuilder()
    cancelar_keyboard.button(text="❌ Cancelar", callback_data="cancelar_deposito")
    keyboard = cancelar_keyboard.as_markup()
    try:
        await message.edit_text(resumen, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await message.answer(resumen, parse_mode="HTML", reply_markup=keyboard)

async def cancelar_deposito_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    mensaje = (
        "<b>❌ Depósito cancelado</b>\n\n"
        "<i>El proceso de depósito ha sido cancelado. Puedes iniciar uno nuevo desde Wallet → Depositar.</i>"
    )
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def procesar_hash_deposito(message: types.Message, state: FSMContext):
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
    await notificar_admins_nuevo_deposito(user_id, cantidad, network_name, deposito_id)
    mensaje_confirmacion = (
        "<b>✅ Depósito registrado</b>\n\n"
        f"<b>ID de Depósito:</b> <code>{deposito_id}</code>\n"
        f"<b>Red:</b> {network_name}\n"
        f"<b>Dirección:</b> <code>{address}</code>\n"
        f"<b>Cantidad:</b> <code>{cantidad:.3f}</code> TON\n"
        f"<b>Hash:</b> <code>{hash_text}</code>\n"
        "<b>Estado:</b> <b>Pendiente de revisión</b>\n"
        "<b>⏰ Tiempo estimado:</b> 24-48 horas\n\n"
        "Guarda este ID para cualquier reporte o consulta.\n"
        "Puedes consultar el estado con: <code>/estado [id]</code>\n\n"
        "Te notificaremos cuando el admin revise tu depósito."
    )
    try:
        await message.edit_text(mensaje_confirmacion, parse_mode="HTML")
    except Exception:
        await message.answer(mensaje_confirmacion, parse_mode="HTML")
    await state.clear()

async def cancelar_retiro_total_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    mensaje = (
        "<b>❌ Retiro cancelado</b>\n\n"
        "<i>El proceso de retiro ha sido cancelado. Puedes iniciar uno nuevo desde Wallet → Retirar.</i>"
    )
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def estado_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.answer("<b>Uso:</b> /estado <ID_de_operacion>", parse_mode="HTML")
        return
    op_id = args[1].strip()
    try:
        if len(op_id) == 24:
            obj_id = bson.ObjectId(op_id)
            dep = await depositos_col.find_one({"_id": obj_id, "user_id": user_id})
            if dep:
                mensaje = (
                    "<b>🔎 Estado de tu Depósito</b>\n\n"
                    f"<b>ID:</b> <code>{op_id}</code>\n"
                    f"<b>Cantidad:</b> <b>{float(dep.get('cantidad', 0)):.3f}</b> {dep.get('network_name', 'TON').split()[-1]}\n"
                    f"<b>Estado:</b> <b>{dep.get('estado', '?')}</b>\n"
                    f"<b>Fecha:</b> {dep.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if dep.get('fecha') else '-'}\n"
                    f"<b>Hash:</b> <code>{dep.get('hash', '-')}</code>\n"
                )
                await message.answer(mensaje, parse_mode="HTML")
                return
            ret = await creditos_col.find_one({"_id": obj_id, "user_id": user_id})
            if ret:
                mensaje = (
                    "<b>🔎 Estado de tu Retiro</b>\n\n"
                    f"<b>ID:</b> <code>{op_id}</code>\n"
                    f"<b>Cantidad:</b> <b>{float(ret.get('cantidad', 0)):.3f}</b> TON\n"
                    f"<b>Estado:</b> <b>{ret.get('estado', '?')}</b>\n"
                    f"<b>Fecha:</b> {ret.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if ret.get('fecha') else '-'}\n"
                    f"<b>Wallet:</b> <code>{ret.get('wallet', '-')}</code>\n"
                )
                await message.answer(mensaje, parse_mode="HTML")
                return
    except Exception:
        pass
    await message.answer("<b>❌ No se encontró ninguna operación con ese ID asociada a tu cuenta.</b>", parse_mode="HTML")

def register_wallet_handlers(dp):
    dp.callback_query.register(cancelar_deposito_handler, lambda c: c.data == "cancelar_deposito")
    dp.callback_query.register(cancelar_retiro_total_handler, lambda c: c.data == "cancelar_retiro_total")
    dp.message.register(estado_handler, lambda m: m.text.startswith("/estado"))