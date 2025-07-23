from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import httpx
from modules.commands import mostrar_promo_paquete_bienvenida

# Estados para FSM
class WalletStates(StatesGroup):
    waiting_for_wallet = State()  # Esperando dirección de wallet
    waiting_for_amount = State()  # Esperando cantidad a retirar
    waiting_for_hash = State()    # Esperando hash de transacción

# Diccionario para controlar usuarios que pueden usar /hash
usuarios_hash_activo = {}  # {user_id: network_key}
# Diccionario para controlar usuarios que están agregando wallet
usuarios_agregando_wallet = {}  # {user_id: True}

class WalletAddresses:
    """Clase para almacenar las direcciones de wallet de cada red"""
    
    def __init__(self):
        # Direcciones de depósito para cada red
        self.addresses = {
            "usdt_bep20": "0xca1BEE70DA9c00b7cB61AA145F3BEFFbCAe4CC0F",  
            "usdt_ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9", 
            "ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9", 
            "trx_trc20": "TGhQFGDDhKJE79rQTgZ2QS5LP4KnoLQkc6" 
        }
    
    def get_address(self, network: str) -> str:
        """Obtener la dirección de una red específica"""
        return self.addresses.get(network, "Dirección no disponible")
    
    def get_all_addresses(self) -> dict:
        """Obtener todas las direcciones"""
        return self.addresses.copy()

# Instancia global de las direcciones
wallet_addresses = WalletAddresses()

async def wallet_handler(message: types.Message):
    balance_ton = 0.0  # Reemplazar con balance real de la base de datos
    mensaje = (
        f"<b>👛 Wallet</b>\n\n"
        f"<i>Gestiona tus fondos en <b>Mundo Mítico.</b>\n\n"
        f"<b>💰 Balance:</b> {balance_ton} TON\n\n"
        f"<blockquote expandable>Deposita para invertir en héroes y criaturas\n— Retira tus ganancias cuando lo desees</blockquote>\n\n"
        f"<b>Selecciona una opción para continuar.</b></i>"
    )
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Depositar", callback_data="wallet_depositar"),
         InlineKeyboardButton(text="📤 Retirar", callback_data="wallet_retirar")]
    ])
    await message.answer(mensaje, parse_mode="HTML", reply_markup=wallet_keyboard)
    await mostrar_promo_paquete_bienvenida(message, message.from_user.id)

async def wallet_depositar_handler(callback: types.CallbackQuery):
    mensaje = (
        "<b>📥 Depositar</b>\n\n"
        "<i><b>Redes disponibles para depositos:</b>\n\n"
        "— USDT Bep20\n"
        "— USDT TON\n"
        "— TON\n"
        "— TRX Trc20\n\n"
        "<b>⚠️ Mínimo:</b> 0.5 TON equivalente en USD\n\n"
        "<b>Selecciona la red para obtener la dirección de depósito.</b></i>"
    )
    depositar_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="USDT Bep20", callback_data="depositar_usdt_bep20"),
         InlineKeyboardButton(text="USDT TON", callback_data="depositar_usdt_ton")],
        [InlineKeyboardButton(text="TON", callback_data="depositar_ton"),
         InlineKeyboardButton(text="TRX Trc20", callback_data="depositar_trx")]
    ])
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=depositar_keyboard)
    await callback.answer()

async def obtener_precios():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "the-open-network,tether,tron",
        "vs_currencies": "usd"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        precio_ton = data.get("the-open-network", {}).get("usd")
        precio_usdt = data.get("tether", {}).get("usd")
        precio_trx = data.get("tron", {}).get("usd")
        return precio_ton, precio_usdt, precio_trx

async def handle_deposit_network(callback: types.CallbackQuery, state: FSMContext):
    """Manejar la selección de red para depósito"""
    network_map = {
        "depositar_usdt_bep20": ("USDT Bep20", "usdt_bep20"),
        "depositar_usdt_ton": ("USDT TON", "usdt_ton"),
        "depositar_ton": ("TON", "ton"),
        "depositar_trx": ("TRX Trc20", "trx_trc20")
    }
    
    callback_data = callback.data
    if callback_data in network_map:
        network_name, network_key = network_map[callback_data]
        address = wallet_addresses.get_address(network_key)
        
        precio_ton, precio_usdt, precio_trx = await obtener_precios()
        min_ton = 0.5
        min_usdt = min_ton * precio_ton if precio_ton else "?"
        min_trx = min_usdt / precio_trx if precio_trx else "?"

        # Mostrar siempre el equivalente en las tres monedas
        minimo = f"{min_ton} TON"
        if network_key.startswith("usdt"):
            minimo = f"{min_usdt:.2f} USDT"
        elif network_key == "trx_trc20":
            minimo = f"{min_trx:.2f} TRX"

        mensaje = (
            f"<b>📥 Depositar {network_name}</b>\n\n"
            f"<i><b>Dirección:</b>\n"
            f"<blockquote><code>{address}</code></blockquote>\n\n"
            f"<b>⚠️ Importante:</b>\n"
            f"— Solo envía {network_name} a esta dirección\n"
            f"— Mínimo: {minimo}\n"
            f"— Los fondos se acreditarán automaticamente\n\n"
            f"<b>📝 Para confirmar tu pago:</b>\n"
            f"1️⃣ Comentario, pon tu ID: <code>{callback.from_user.id}</code>(Recomendado)\n"
            f"2️⃣ Después de enviar, usa el comando: <code>/hash [tu_hash_aqui]</code></i>"
        )
        
        # Guardar datos en el estado FSM
        await state.update_data(network_name=network_name, network_key=network_key, address=address)
        # Cambiar al estado de espera de hash
        await state.set_state(WalletStates.waiting_for_hash)
        
        copy_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="wallet_depositar")]
        ])
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=copy_keyboard)
    else:
        await callback.answer("Red no válida")
    

async def wallet_retirar_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    balance_ton = 0.0  # Reemplazar con balance real de la base de datos
    min_retiro = 1.1
    
    # Lógica if-elif-else para diferentes casos
    if balance_ton < min_retiro:
        mensaje = (
            f"<b>📤 Retirar</b>\n\n"
            f"<i><b>💰 Balance actual:</b> {balance_ton} TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> {min_retiro} TON\n\n"
            f"<b>❌ No puedes retirar</b>\n"
            f"Tu balance es insuficiente para realizar un retiro.\n\n"
            f"<b>💡 Consejo:</b> Deposita más fondos o espera a que tus criaturas generen más ganancias.</i>"
        )
        await callback.message.answer(mensaje, parse_mode="HTML")
    elif balance_ton == 0:
        mensaje = (
            f"<b>📤 Retirar</b>\n\n"
            f"<i><b>💰 Balance actual:</b> {balance_ton} TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> {min_retiro} TON\n\n"
            f"<b>❌ Balance vacío</b>\n"
            f"No tienes fondos disponibles para retirar.\n\n"
            f"<b>💡 Consejo:</b> Primero debes depositar fondos o comprar criaturas para generar ganancias.</i>"
        )
        await callback.message.answer(mensaje, parse_mode="HTML")
    else:
        mensaje = (
            f"<b>📤 Retirar</b>\n\n"
            f"<i><b>💰 Balance actual:</b> {balance_ton} TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> {min_retiro} TON\n\n"
            f"<b>✅ Puedes retirar</b>\n"
            f"Tu balance es suficiente para realizar un retiro.\n\n"
            f"<b>📝 Para retirar:</b>\n"
            f"1️⃣ Envía tu dirección de wallet TON\n"
            f"2️⃣ Especifica la cantidad a retirar\n\n"
            f"<b>🔗 Red disponible:</b> TON</i>"
        )
        
        # Guardar el balance en el estado FSM
        await state.update_data(balance=balance_ton, min_retiro=min_retiro)
        # Cambiar al estado de espera de wallet
        await state.set_state(WalletStates.waiting_for_wallet)
        
        await callback.message.answer(mensaje, parse_mode="HTML")
    
    await callback.answer()



async def procesar_hash_pago(message: types.Message, state: FSMContext):
    """Procesar el hash de pago enviado por el usuario"""
    user_id = message.from_user.id
    
    # Verificar que el usuario esté en el estado correcto
    current_state = await state.get_state()
    if current_state != WalletStates.waiting_for_hash.state:
        await message.answer(
            "<b>❌ Comando no disponible</b>\n\n"
            "<i>El comando /hash solo está disponible cuando confirmas un pago.\n"
            "Ve a Wallet → Depositar → Selecciona red</i>",
            parse_mode="HTML"
        )
        return
    
    # Extraer el hash del comando /hash [hash]
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.answer(
            "<b>❌ Error</b>\n\n"
            "<i>Formato incorrecto. Usa:\n"
            "<code>/hash [tu_hash_aqui]</code></i>",
            parse_mode="HTML"
        )
        return
    
    hash_text = command_parts[1].strip()
    
    # Obtener datos del estado FSM
    data = await state.get_data()
    network_name = data.get('network_name', 'desconocida')
    network_key = data.get('network_key', 'desconocida')
    address = data.get('address', '')
    
    # Aquí puedes agregar validación del hash según la red
    # Por ejemplo, verificar formato, longitud, etc.
    
    mensaje_confirmacion = (
        f"<b>📋 Hash Recibido</b>\n\n"
        f"<i><b>🔗 Red:</b> {network_name}\n"
        f"<b>📍 Dirección:</b> <code>{address}</code>\n"
        f"<b>🔍 Hash:</b> <code>{hash_text}</code>\n\n"
        f"<b>✅ Estado:</b> Pendiente de revisión\n"
        f"<b>⏰ Tiempo estimado:</b> 24-48 horas\n\n"
        f"Te notificaremos cuando el admin revise tu depósito.</i>"
    )
    
    # Aquí podrías guardar el hash en la base de datos
    # await guardar_hash_pago(user_id, hash_text, network_key, network_name, address)
    
    await message.answer(mensaje_confirmacion, parse_mode="HTML")
    
    # Limpiar el estado FSM
    await state.clear()
    
    # Opcional: Notificar al admin sobre el nuevo depósito
    # await notificar_admin_deposito(user_id, hash_text, network_key, network_name)

async def procesar_cantidad_retiro(message: types.Message, state: FSMContext):
    """Procesar la cantidad de retiro enviada por el usuario"""
    user_id = message.from_user.id
    cantidad_text = message.text.strip()
    
    # Verificar que el usuario esté en el estado correcto
    current_state = await state.get_state()
    if current_state != WalletStates.waiting_for_amount.state:
        return
    
    # Validar que sea un número válido
    try:
        cantidad = float(cantidad_text)
        if cantidad <= 0:
            raise ValueError("Cantidad debe ser mayor a 0")
    except ValueError:
        await message.answer(
            "<b>❌ Cantidad inválida</b>\n\n"
            "<i>Por favor envía un número válido mayor a 0.\n"
            "<b>Ejemplo:</b> <code>1.5</code> o <code>2.0</code></i>",
            parse_mode="HTML"
        )
        return
    
    # Obtener datos del estado
    data = await state.get_data()
    balance = data.get('balance', 0)
    min_retiro = data.get('min_retiro', 1.1)
    wallet_address = data.get('wallet_address', '')
    
    # Validar cantidad vs balance y mínimo
    if cantidad < min_retiro:
        await message.answer(
            f"<b>❌ Cantidad insuficiente</b>\n\n"
            f"<i>La cantidad mínima de retiro es <b>{min_retiro} TON</b>.\n"
            f"Tu solicitud: <b>{cantidad} TON</b></i>",
            parse_mode="HTML"
        )
        return
    
    if cantidad > balance:
        await message.answer(
            f"<b>❌ Balance insuficiente</b>\n\n"
            f"<i>Tu balance disponible es <b>{balance} TON</b>.\n"
            f"Tu solicitud: <b>{cantidad} TON</b></i>",
            parse_mode="HTML"
        )
        return
    
    # Guardar la cantidad en el estado FSM
    await state.update_data(cantidad=cantidad)
    
    # Crear mensaje de confirmación
    mensaje_confirmacion = (
        f"<b>📋 Confirmar Retiro</b>\n\n"
        f"<i><b>💰 Cantidad:</b> {cantidad} TON\n"
        f"<b>📍 Wallet:</b> <code>{wallet_address}</code>\n\n"
        f"<b>✅ Confirmar retiro</b>\n"
        f"Tu solicitud será procesada en 24-48 horas.\n\n"
        f"<b>⚠️ Importante:</b>\n"
        f"— Verifica que la dirección sea correcta\n"
        f"— El retiro se procesará automáticamente\n"
        f"— Recibirás notificación cuando se complete</i>"
    )
    
    # Crear botones de confirmación
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirmar", callback_data="confirmar_retiro")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancelar_retiro")]
    ])
    
    await message.answer(mensaje_confirmacion, parse_mode="HTML", reply_markup=confirm_keyboard)
    
    # Limpiar el estado FSM
    await state.clear()

async def procesar_wallet_ton(message: types.Message, state: FSMContext):
    """Procesar la dirección de wallet TON enviada por el usuario"""
    user_id = message.from_user.id
    wallet_address = message.text.strip()
    
    # Verificar que el usuario esté en el estado correcto
    current_state = await state.get_state()
    if current_state != WalletStates.waiting_for_wallet.state:
        await message.answer(
            "<b>❌ Comando no disponible</b>\n\n"
            "<i>Para agregar tu wallet TON, ve a Wallet → Retirar</i>",
            parse_mode="HTML"
        )
        return
    
    # Validación básica de dirección TON
    if not wallet_address.startswith("UQ") or len(wallet_address) < 48:
        await message.answer(
            "<b>❌ Dirección inválida</b>\n\n"
            "<i>La dirección de wallet TON debe comenzar con 'UQ' y tener al menos 48 caracteres.\n"
            "Asegúrate de copiar la dirección completa de tu wallet TON.</i>",
            parse_mode="HTML"
        )
        return
    
    # Guardar la dirección en el estado FSM
    await state.update_data(wallet_address=wallet_address)
    
    # Cambiar al estado de espera de cantidad
    await state.set_state(WalletStates.waiting_for_amount)
    
    # Obtener datos del estado
    data = await state.get_data()
    balance = data.get('balance', 0)
    min_retiro = data.get('min_retiro', 1.1)
    
    mensaje = (
        f"<b>✅ Wallet TON Registrada</b>\n\n"
        f"<i>Tu dirección ha sido guardada:\n\n"
        f"<code>{wallet_address}</code>\n\n"
        f"<b>💰 Balance disponible:</b> {balance} TON\n"
        f"<b>⚠️ Mínimo de retiro:</b> {min_retiro} TON\n\n"
        f"<b>📝 Próximo paso:</b>\n"
        f"Envía la cantidad que deseas retirar (en TON)\n\n"
        f"<b>Ejemplo:</b> <code>1.5</code> o <code>2.0</code></i>"
    )
    
    await message.answer(mensaje, parse_mode="HTML") 

async def confirmar_retiro_handler(callback: types.CallbackQuery):
    """Handler para confirmar retiro"""
    await callback.message.edit_text(
        "<b>✅ Retiro Confirmado</b>\n\n"
        "<i>Tu solicitud de retiro ha sido procesada.\n\n"
        "<b>⏰ Tiempo estimado:</b> 24-48 horas\n"
        "<b>📧 Notificación:</b> Recibirás confirmación cuando se complete</i>",
        parse_mode="HTML"
    )
    await callback.answer()

async def cancelar_retiro_handler(callback: types.CallbackQuery):
    """Handler para cancelar retiro"""
    await callback.message.edit_text(
        "<b>❌ Retiro Cancelado</b>\n\n"
        "<i>Tu solicitud de retiro ha sido cancelada.\n\n"
        "Puedes iniciar un nuevo retiro desde Wallet → Retirar</i>",
        parse_mode="HTML"
    )
    await callback.answer() 