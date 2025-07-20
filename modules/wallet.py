from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import httpx

# Diccionario para controlar usuarios que pueden usar /hash
usuarios_hash_activo = {}  # {user_id: network_key}
# Diccionario para controlar usuarios que están agregando wallet
usuarios_agregando_wallet = {}  # {user_id: True}

class WalletAddresses:
    """Clase para almacenar las direcciones de wallet de cada red"""
    
    def __init__(self):
        # Direcciones de depósito para cada red
        self.addresses = {
            "usdt_bep20": "0xca1BEE70DA9c00b7cB61AA145F3BEFFbCAe4CC0F",  # Reemplazar con dirección real
            "usdt_ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9",  # Reemplazar con dirección real
            "ton": "UQBI9sAHogkSdCIipmakzc_Kt2mpILqGjSdXPHxtnhTEKE-9",  # Reemplazar con dirección real
            "trx_trc20": "TGhQFGDDhKJE79rQTgZ2QS5LP4KnoLQkc6"  # Reemplazar con dirección real
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
        f"<i><b>👛 Wallet</b>\n\n"
        f"Gestiona tus fondos en <b>Mundo Mítico.</b>\n\n"
        f"<b>💰 Balance:</b> {balance_ton} TON\n\n"
        f"<blockquote expandable>Deposita para invertir en héroes y criaturas\n— Retira tus ganancias cuando lo desees</blockquote>\n\n"
        f"<b>Selecciona una opción para continuar.</b></i>"
    )
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Depositar", callback_data="wallet_depositar"),
         InlineKeyboardButton(text="Retirar", callback_data="wallet_retirar")]
    ])
    await message.answer(mensaje, parse_mode="HTML", reply_markup=wallet_keyboard)

async def wallet_depositar_handler(callback: types.CallbackQuery):
    mensaje = (
        "<i><b>📥 Depositar\n\n"
        "Redes disponibles para depositos:</b>\n\n"
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

async def handle_deposit_network(callback: types.CallbackQuery):
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
            f"<i><b>📥 Depositar {network_name}</b>\n\n"
            f"<b>Dirección:</b>\n"
            f"<blockquote><code>{address}</code></blockquote>\n\n"
            f"<b>⚠️ Importante:</b>\n"
            f"— Solo envía {network_name} a esta dirección\n"
            f"— Mínimo: {minimo}\n"
            f"— Los fondos se acreditarán automaticamente\n\n"
            f"<b>📝 Para confirmar tu pago:</b>\n"
            f"1️⃣ Comentario, pon tu ID: <code>{callback.from_user.id}</code>\n"
            f"2️⃣ Usa: <code>/hash tu_hash_aqui</code></i>"
        )
        
        copy_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="wallet_depositar")]
        ])
        
        # Activar el comando /hash para este usuario
        user_id = callback.from_user.id
        usuarios_hash_activo[user_id] = network_key
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=copy_keyboard)
    else:
        await callback.answer("Red no válida")
    

async def wallet_retirar_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance_ton = 0.0  # Reemplazar con balance real de la base de datos
    min_retiro = 1.1
    
    # Lógica if-elif-else para diferentes casos
    if balance_ton < min_retiro:
        mensaje = (
            f"<i><b>📤 Retirar</b>\n\n"
            f"<b>💰 Balance actual:</b> {balance_ton} TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> {min_retiro} TON\n\n"
            f"<b>❌ No puedes retirar</b>\n"
            f"Tu balance es insuficiente para realizar un retiro.\n\n"
            f"<b>💡 Consejo:</b> Deposita más fondos o espera a que tus criaturas generen más ganancias.</i>"
        )
    elif balance_ton == 0:
        mensaje = (
            f"<i><b>📤 Retirar</b>\n\n"
            f"<b>💰 Balance actual:</b> {balance_ton} TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> {min_retiro} TON\n\n"
            f"<b>❌ Balance vacío</b>\n"
            f"No tienes fondos disponibles para retirar.\n\n"
            f"<b>💡 Consejo:</b> Primero debes depositar fondos o comprar criaturas para generar ganancias.</i>"
        )
    else:
        mensaje = (
            f"<i><b>📤 Retirar</b>\n\n"
            f"<b>💰 Balance actual:</b> {balance_ton} TON\n"
            f"<b>⚠️ Mínimo de retiro:</b> {min_retiro} TON\n\n"
            f"<b>✅ Puedes retirar</b>\n"
            f"Tu balance es suficiente para realizar un retiro.\n\n"
            f"<b>📝 Para retirar:</b>\n"
            f"1️⃣ Envía tu dirección de wallet TON\n"
            f"2️⃣ Especifica la cantidad a retirar\n\n"
            f"<b>🔗 Red disponible:</b> TON</i>"
        )
        
        # Activar el proceso de agregar wallet para este usuario
        usuarios_agregando_wallet[user_id] = True
    
    await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer() 



async def procesar_hash_pago(message: types.Message):
    """Procesar el hash de pago enviado por el usuario"""
    user_id = message.from_user.id
    
    # Verificar si el usuario tiene el comando /hash activo
    if user_id not in usuarios_hash_activo:
        await message.answer(
            "<b>❌ Comando no disponible</b>\n\n"
            "<i>El comando /hash solo está disponible cuando confirmas un pago.\n"
            "Ve a Wallet → Depositar → Selecciona red → Confirmar Pago</i>",
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
    
    # Aquí puedes agregar validación del hash según la red
    # Por ejemplo, verificar formato, longitud, etc.
    
    mensaje_confirmacion = (
        f"<b>📋 Hash Recibido</b>\n\n"
        f"<i>Tu hash ha sido registrado:\n\n"
        f"<code>{hash_text}</code>\n\n"
        f"<b>✅ Estado:</b> Pendiente de revisión\n"
        f"<b>⏰ Tiempo estimado:</b> 24-48 horas\n\n"
        f"Te notificaremos cuando el admin revise tu depósito.</i>"
    )
    
    # Obtener la red del usuario
    network_key = usuarios_hash_activo.get(user_id, "desconocida")
    
    # Aquí podrías guardar el hash en la base de datos
    # await guardar_hash_pago(user_id, hash_text, network_key, etc.)
    
    await message.answer(mensaje_confirmacion, parse_mode="HTML")
    
    # Desactivar el comando /hash para este usuario
    usuarios_hash_activo.pop(user_id, None)
    
    # Opcional: Notificar al admin sobre el nuevo depósito
    # await notificar_admin_deposito(user_id, hash_text, network_key) 

async def procesar_wallet_ton(message: types.Message):
    """Procesar la dirección de wallet TON enviada por el usuario"""
    user_id = message.from_user.id
    wallet_address = message.text.strip()
    
    # Verificar si el usuario está en proceso de agregar wallet
    if user_id not in usuarios_agregando_wallet:
        await message.answer(
            "<b>❌ Comando no disponible</b>\n\n"
            "<i>Para agregar tu wallet TON, ve a Wallet → Retirar</i>",
            parse_mode="HTML"
        )
        return
    
    # Validación básica de dirección (puedes hacerla más específica)
    if len(wallet_address) < 10:
        await message.answer(
            "<b>❌ Dirección inválida</b>\n\n"
            "<i>La dirección de wallet parece ser muy corta.\n"
            "Asegúrate de copiar la dirección completa.</i>",
            parse_mode="HTML"
        )
        return
    
    mensaje_confirmacion = (
        f"<b>✅ Wallet TON Registrada</b>\n\n"
        f"<i>Tu dirección ha sido guardada:\n\n"
        f"<code>{wallet_address}</code>\n\n"
        f"<b>📝 Próximos pasos:</b>\n"
        f"1️⃣ Especifica la cantidad a retirar\n"
        f"2️⃣ El admin revisará tu solicitud\n"
        f"3️⃣ Recibirás la confirmación\n\n"
        f"<b>⚠️ Importante:</b>\n"
        f"— Solo se aceptan direcciones TON\n"
        f"— El admin verificará la dirección\n"
        f"— Los retiros se procesan en 24-48 horas</i>"
    )
    
    # Aquí podrías guardar la dirección en la base de datos
    # await guardar_wallet_ton(user_id, wallet_address)
    
    await message.answer(mensaje_confirmacion, parse_mode="HTML")
    
    # Desactivar el proceso de agregar wallet
    usuarios_agregando_wallet.pop(user_id, None)
    
    # Opcional: Notificar al admin sobre la nueva wallet
    # await notificar_admin_wallet(user_id, wallet_address) 