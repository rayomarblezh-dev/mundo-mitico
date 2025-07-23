from utils.database import usuarios_col
import logging

# Diccionario de criaturas y NFTs realmente disponibles en el bot
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
    return EMOJIS_INVENTARIO.get(item.lower(), "📦")

def obtener_nombre(item: str) -> str:
    return NOMBRES_INVENTARIO.get(item.lower(), item.capitalize())

async def obtener_inventario_usuario(user_id: int) -> dict:
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        return {}
    return usuario.get("inventario", {})

async def mostrar_inventario_usuario(event, user_id: int):
    inventario = await obtener_inventario_usuario(user_id)
    if not inventario or all(cantidad == 0 for cantidad in inventario.values()):
        texto = "<b>🧳 Inventario</b>\n\n<i>Tu inventario está vacío. ¡Captura criaturas o compra NFTs para llenarlo!</i>"
    else:
        texto = "<b>🧳 Inventario</b>\n\n"
        for item, cantidad in inventario.items():
            if cantidad > 0:
                emoji = obtener_emoji(item)
                nombre = obtener_nombre(item)
                texto += f"{emoji} <b>{nombre}</b>: <code>{cantidad}</code>\n"
    try:
        # Si es callback_query
        if hasattr(event, 'message') and hasattr(event, 'edit_text'):
            try:
                await event.message.edit_text(texto, parse_mode="HTML")
                logging.info(f"Inventario editado para user_id={user_id}")
            except Exception as e:
                logging.warning(f"Fallo edit_text, usando answer para user_id={user_id}: {e}")
                await event.message.answer(texto, parse_mode="HTML")
        # Si es mensaje directo
        elif hasattr(event, 'answer'):
            await event.answer(texto, parse_mode="HTML")
            logging.info(f"Inventario respondido con answer para user_id={user_id}")
        else:
            await event.answer(texto)
            logging.info(f"Inventario respondido con answer (fallback) para user_id={user_id}")
    except Exception as e:
        logging.error(f"Error mostrando inventario para user_id={user_id}: {e}")
        if hasattr(event, 'message'):
            await event.message.answer("<b>⚠️ Error</b>\n\n<i>Ocurrió un error mostrando tu inventario. Intenta de nuevo más tarde.</i>", parse_mode="HTML")
        elif hasattr(event, 'answer'):
            await event.answer("<b>⚠️ Error</b>\n\n<i>Ocurrió un error mostrando tu inventario. Intenta de nuevo más tarde.</i>", parse_mode="HTML")