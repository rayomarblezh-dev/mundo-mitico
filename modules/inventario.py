import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import obtener_inventario_usuario, obtener_balance_usuario, usuarios_col
from modules.constants import (
    CRIATURAS_CONFIG,
    NFTS_CONFIG,
    GANANCIAS_DIARIAS_NFTS,
    NFT_INVENTARIO_MAP,
    obtener_emoji_item,
    obtener_nombre_item,
    obtener_ganancia_diaria_item,
    es_nft,
    es_criatura,
    obtener_categoria_item
)

logger = logging.getLogger(__name__)

def formatear_inventario(inventario: dict) -> tuple[str, float]:
    """Genera el texto del inventario y calcula la ganancia total usando configuración centralizada."""
    texto = "<b>🧳 Inventario</b>\n\n"
    total_ganancia = 0.0
    items_con_ganancia = []
    items_sin_ganancia = []
    
    # Separar items con y sin ganancia
    for item, cantidad in inventario.items():
        if cantidad > 0:
            emoji = obtener_emoji_item(item)
            nombre = obtener_nombre_item(item)
            ganancia = obtener_ganancia_diaria_item(item)
            
            if ganancia > 0:
                items_con_ganancia.append((item, cantidad, emoji, nombre, ganancia))
                total_ganancia += ganancia * cantidad
            else:
                items_sin_ganancia.append((item, cantidad, emoji, nombre))
    
    # Mostrar primero items con ganancia (NFTs)
    if items_con_ganancia:
        texto += "<b>💰 Items con ganancia diaria:</b>\n"
        for item, cantidad, emoji, nombre, ganancia in items_con_ganancia:
            texto += f"{emoji} <b>{nombre}</b>: <code>{cantidad}</code> <i>(+{ganancia:.3f} TON/día c/u)</i>\n"
        texto += "\n"
    
    # Mostrar items sin ganancia (criaturas)
    if items_sin_ganancia:
        texto += "<b>🎯 Items de colección:</b>\n"
        for item, cantidad, emoji, nombre in items_sin_ganancia:
            texto += f"{emoji} <b>{nombre}</b>: <code>{cantidad}</code>\n"
    
    if total_ganancia > 0:
        texto += f"\n<b>💸 Ganancia diaria total: <code>{total_ganancia:.3f} TON</code></b>"
    
    return texto, total_ganancia

async def mostrar_inventario_usuario(event, user_id: int):
    """Muestra el inventario del usuario de forma elegante y robusta."""
    try:
        # Obtener inventario y balance
        inventario = await obtener_inventario_usuario(user_id)
        
        # Crear mensaje principal
        mensaje = (
            "<b>🧳 Inventario</b>\n\n"
        )
        
        if not inventario or all(cantidad == 0 for cantidad in inventario.values()):
            mensaje += "Tu inventario está vacío. ¡Captura criaturas o compra NFTs para llenarlo!\n\n"
            mensaje += "Consejos:\n"
            mensaje += "• Compra criaturas en la Tienda\n"
            mensaje += "• Participa en Explorar para ganar recompensas\n"
            mensaje += "• Invierte en NFTs para ganancias diarias"
        else:
            texto_inventario, ganancia_total = formatear_inventario(inventario)
            mensaje += texto_inventario
            
            if ganancia_total > 0:
                mensaje += f"\n\nProyección mensual: {ganancia_total * 30:.3f} TON"
        
        # Crear teclado con botón de volver
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Volver", callback_data="perfil")
        keyboard = builder.as_markup()
        
        # Enviar mensaje según el tipo de evento
        if hasattr(event, 'data'):  # Es un callback
            try:
                await event.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
            except Exception as e:
                if "message is not modified" in str(e):
                    # El mensaje es el mismo, solo responder al callback
                    await event.answer()
                else:
                    # Otro error, intentar enviar nuevo mensaje
                    await event.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
        else:  # Es un mensaje
            await event.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
        
        logger.info(f"Inventario mostrado exitosamente para user_id={user_id}")
        
    except Exception as e:
        logger.error(f"Error mostrando inventario para user_id={user_id}: {e}")
        mensaje_error = (
            "⚠️ Error\n\n"
            "Ocurrió un error mostrando tu inventario. Intenta de nuevo más tarde."
        )
        
        try:
            if hasattr(event, 'data'):  # Es un callback
                await event.answer(mensaje_error, show_alert=True)
            else:  # Es un mensaje
                await event.answer(mensaje_error, parse_mode="HTML")
        except Exception:
            pass

async def inventario_detallado_handler(callback: types.CallbackQuery):
    """Handler para mostrar inventario detallado con estadísticas"""
    user_id = callback.from_user.id
    
    try:
        inventario = await obtener_inventario_usuario(user_id)
        balance = await obtener_balance_usuario(user_id)
        
        # Calcular estadísticas
        total_items = sum(inventario.values())
        items_unicos = len([item for item, cantidad in inventario.items() if cantidad > 0])
        ganancia_total = sum(obtener_ganancia_diaria_item(item) * cantidad 
                           for item, cantidad in inventario.items())
        
        mensaje = (
            "📊 Inventario Detallado\n\n"
            f"Balance: {balance:.3f} TON\n"
            f"Total de items: {total_items}\n"
            f"Items únicos: {items_unicos}\n"
            f"Ganancia diaria: {ganancia_total:.3f} TON\n\n"
        )
        
        if inventario:
            mensaje += "Desglose por categoría:\n\n"
            
            # Criaturas
            criaturas = {k: v for k, v in inventario.items() 
                        if es_criatura(k) and v > 0}
            if criaturas:
                mensaje += "🐾 Criaturas:\n"
                for item, cantidad in criaturas.items():
                    emoji = obtener_emoji_item(item)
                    nombre = obtener_nombre_item(item)
                    categoria = obtener_categoria_item(item)
                    mensaje += f"  {emoji} {nombre} ({categoria}): {cantidad}\n"
                mensaje += "\n"
            
            # NFTs
            nfts = {k: v for k, v in inventario.items() 
                   if es_nft(k) and v > 0}
            if nfts:
                mensaje += "💎 NFTs:\n"
                for item, cantidad in nfts.items():
                    emoji = obtener_emoji_item(item)
                    nombre = obtener_nombre_item(item)
                    ganancia = obtener_ganancia_diaria_item(item)
                    categoria = obtener_categoria_item(item)
                    mensaje += f"  {emoji} {nombre} ({categoria}): {cantidad} (+{ganancia:.3f} TON/día)\n"
        else:
            mensaje += "Tu inventario está vacío."
        
        # Botón para volver
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="inventario_volver")]
        ])
        
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error en inventario detallado para user_id={user_id}: {e}")
        await callback.answer("❌ Error mostrando inventario detallado", show_alert=True)

async def volver_inventario_handler(callback: types.CallbackQuery):
    """Handler para volver al inventario principal"""
    user_id = callback.from_user.id
    await mostrar_inventario_usuario(callback, user_id)
    await callback.answer()



def register_inventario_handlers(dp):
    """Registra los handlers relacionados con el inventario."""
    # Callbacks de inventario
    dp.callback_query.register(inventario_detallado_handler, lambda c: c.data == "inventario_detallado")
    dp.callback_query.register(volver_inventario_handler, lambda c: c.data == "inventario_volver")
