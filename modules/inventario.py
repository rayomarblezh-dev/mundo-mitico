from utils.database import usuarios_col
import logging
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Diccionario de criaturas y NFTs disponibles en el bot
EMOJIS_INVENTARIO = {
    "hada": "🧚",
    "mago": "🧙‍♂️",
    "dragon": "🐉",
    "orco": "👹",
    "gremnli": "👺",
    "unicornio": "🦄",
    "genio": "🧞",
    "kraken": "👾",
    "licantropo": "🐺",
    # NFTs
    "moguri-nft": "💀",
    "gargola-nft": "🦇",
    "ghost-nft": "👻",
}

NOMBRES_INVENTARIO = {
    "hada": "Hada",
    "mago": "Mago",
    "dragon": "Dragón",
    "orco": "Orco",
    "gremnli": "Gremnli",
    "unicornio": "Unicornio",
    "genio": "Genio",
    "kraken": "Kraken",
    "licantropo": "Licántropo",
    # NFTs
    "moguri-nft": "Moguri-NFT",
    "gargola-nft": "Gárgola-NFT",
    "ghost-nft": "Ghost-NFT",
}

def obtener_emoji(item: str) -> str:
    """Devuelve el emoji correspondiente al item, o una caja si no existe."""
    return EMOJIS_INVENTARIO.get(item.lower(), "📦")

def obtener_nombre(item: str) -> str:
    """Devuelve el nombre legible del item, o lo capitaliza si no está en el diccionario."""
    return NOMBRES_INVENTARIO.get(item.lower(), item.capitalize())

async def obtener_inventario_usuario(user_id: int) -> dict:
    """Obtiene el inventario del usuario desde la base de datos."""
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return {}
    return usuario.get("inventario", {})

# Tabla de ganancias diarias por NFT y criaturas (solo NFTs por ahora)
GANANCIAS_DIARIAS = {
    "moguri-nft": 0.075,
    "gargola-nft": 0.025,
    "ghost-nft": 0.2,
    # Puedes agregar criaturas aquí si lo deseas, por ejemplo: "hada": 0.01,
}

def crear_teclado_volver():
    """Crea el teclado de volver atrás."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="‹ Back")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def formatear_inventario(inventario: dict) -> (str, float):
    """Genera el texto del inventario y calcula la ganancia total."""
    texto = "<b>🧳 Inventario</b>\n\n"
    total_ganancia = 0.0
    for item, cantidad in inventario.items():
        if cantidad > 0:
            emoji = obtener_emoji(item)
            nombre = obtener_nombre(item)
            ganancia = GANANCIAS_DIARIAS.get(item.lower(), 0)
            if ganancia > 0:
                texto += f"{emoji} <b>{nombre}</b>: <code>{cantidad}</code>  <i>(+{ganancia} TON/día c/u)</i>\n"
                total_ganancia += ganancia * cantidad
            else:
                texto += f"{emoji} <b>{nombre}</b>: <code>{cantidad}</code>\n"
    if total_ganancia > 0:
        texto += f"\n<b>💸 Ganancia diaria total: <code>{total_ganancia:.3f} TON</code></b>"
    return texto, total_ganancia

async def mostrar_inventario_usuario(event, user_id: int):
    """Muestra el inventario del usuario de forma elegante y robusta."""
    inventario = await obtener_inventario_usuario(user_id)
    if not inventario or all(cantidad == 0 for cantidad in inventario.values()):
        texto = "<b>🧳 Inventario</b>\n\n<i>Tu inventario está vacío. ¡Captura criaturas o compra NFTs para llenarlo!</i>"
    else:
        texto, _ = formatear_inventario(inventario)
    volver_keyboard = crear_teclado_volver()
    try:
        # Se intenta responder de la mejor manera posible según el tipo de evento
        if hasattr(event, 'message') and hasattr(event, 'edit_text'):
            try:
                await event.message.answer(texto, parse_mode="HTML", reply_markup=volver_keyboard)
                logging.info(f"Inventario mostrado para user_id={user_id}")
            except Exception as e:
                logging.warning(f"Fallo answer para user_id={user_id}: {e}")
                await event.message.answer(texto, parse_mode="HTML", reply_markup=volver_keyboard)
        elif hasattr(event, 'answer'):
            await event.answer(texto, parse_mode="HTML", reply_markup=volver_keyboard)
            logging.info(f"Inventario respondido con answer para user_id={user_id}")
        else:
            await event.answer(texto)
            logging.info(f"Inventario respondido con answer (fallback) para user_id={user_id}")
    except Exception as e:
        logging.error(f"Error mostrando inventario para user_id={user_id}: {e}")
        mensaje_error = "<b>⚠️ Error</b>\n\n<i>Ocurrió un error mostrando tu inventario. Intenta de nuevo más tarde.</i>"
        if hasattr(event, 'message'):
            await event.message.answer(mensaje_error, parse_mode="HTML")
        elif hasattr(event, 'answer'):
            await event.answer(mensaje_error, parse_mode="HTML")

# Handler para el botón de menú '‹ Back' desde inventario
async def back_from_inventario_handler(message: types.Message):
    """Regresa al menú principal (start)."""
    from modules.start import start_handler
    await start_handler(message)

def register_inventario_handlers(dp):
    """Registra los handlers relacionados con el inventario."""
    dp.message.register(back_from_inventario_handler, lambda m: m.text == "‹ Back")