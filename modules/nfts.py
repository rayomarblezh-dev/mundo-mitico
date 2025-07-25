from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
import os
from utils.database import usuario_tiene_nft_comun, usuario_tiene_nft_ghost, comprar_nft, obtener_nft_usuario, procesar_compra_item
import logging

logger = logging.getLogger(__name__)

async def nfts_handler(callback: types.CallbackQuery):
    """Handler para mostrar la sección de NFTs"""
    try:
        await callback.message.delete()
    except Exception:
        pass
    mensaje = (
        "<b>🎨 NFTs</b>\n\n"
        "Los NFTs son colecciones únicas y limitadas de arte digital.\n\n"
        "<blockquote>Cada NFT tiene características especiales y puede generar ganancias diarias en TON.</blockquote>\n\n"
        "<b>⚠️ Importante:</b> Solo puedes tener <b>1 NFT común</b> (Moguri o Gárgola) y <b>1 NFT Ghost</b> a la vez.\n\n"
        "Selecciona un NFT para ver sus detalles y precio."
    )
    volver_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="‹ Back")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
    await callback.answer()

async def nft_moguri_handler(callback: types.CallbackQuery):
    """Handler para el NFT Moguri (común)"""
    mensaje = (
        "<b>💀 Moguri-NFT (Común)</b>\n\n"
        "<i>Un NFT misterioso con poderes ancestrales que genera ganancias diarias.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.5 TON\n"
        "• Ganancia diaria: 0.075 TON\n"
        "• Duración: 16 días\n"
        "• ROI total: 1.2 TON\n"
        "• ROI: 240%\n\n"
        "<b>🎨 Características:</b>\n"
        "— NFT de rareza común\n"
        "— Generación rápida de ganancias\n"
        "— Duración corta de 16 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.5 TON", callback_data="comprar_nft_moguri")]
    ])
    
    # Enviar imagen con caption y solo el botón de comprar
    image_path = os.path.join("images", "moguri.jpg")
    photo = FSInputFile(image_path)
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    except Exception:
        await callback.message.answer_photo(photo, caption=mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def nft_gargola_handler(callback: types.CallbackQuery):
    """Handler para el NFT Gargola (común)"""
    mensaje = (
        "<i><b>🦇 Gargola-NFT (Común)</b>\n\n"
        "Un NFT protector con energía mágica que ofrece ganancias superiores.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1.0 TON\n"
        "• Ganancia diaria: 0.025 TON\n"
        "• Duración: 365 días\n"
        "• ROI total: 9.125 TON\n"
        "• ROI: 912%\n\n"
        "<b>🎨 Características:</b>\n"
        "— NFT de rareza común\n"
        "— Ganancia diaria superior\n"
        "— Duración extendida de 365 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1.0 TON", callback_data="comprar_nft_gargola")]
    ])
    
    # Enviar imagen con caption y solo el botón de comprar
    image_path = os.path.join("images", "gargola.jpg")
    photo = FSInputFile(image_path)
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    except Exception:
        await callback.message.answer_photo(photo, caption=mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def nft_ghost_handler(callback: types.CallbackQuery):
    """Handler para el NFT Ghost =mm(raro)"""
    mensaje = (
        "<i><b>👻 Ghost-NFT (Raro)</b>\n\n"
        "Un NFT etéreo de rareza superior con poderes sobrenaturales.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 3.5 TON\n"
        "• Ganancia diaria: 0.2 TON\n"
        "• Duración: 30 días\n"
        "• ROI total: 6.0 TON\n"
        "• ROI: 171%\n\n"
        "<b>🎨 Características:</b>\n"
        "— NFT de rareza rara\n"
        "— Ganancia diaria muy alta\n"
        "— Duración de 30 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 3.5 TON", callback_data="comprar_nft_ghost")]
    ])
    
    # Enviar imagen con caption y solo el botón de comprar
    image_path = os.path.join("images", "ghost.jpg")
    photo = FSInputFile(image_path)
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    except Exception:
        await callback.message.answer_photo(photo, caption=mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

# Handlers para compra de NFTs
async def comprar_nft_moguri_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item = {"tipo": "nft", "nombre": "Moguri-NFT", "precio": 0.5}
    resultado = await procesar_compra_item(user_id, item)
    if resultado["ok"]:
        mensaje = (
            "<b>✅ ¡Compra exitosa!</b>\n\n"
            "Has adquirido el <b>💀 Moguri-NFT</b>\n\n"
            "<b>💰 Información:</b>\n"
            "• Precio pagado: 0.5 TON\n"
            "• Ganancia diaria: 0.075 TON\n"
            "• Duración: 16 días\n"
            "• ROI total: 1.2 TON\n"
            "• ROI: 240%\n\n"
            "<i>Tu NFT comenzará a generar ganancias automáticamente.</i>"
        )
    else:
        mensaje = f"<b>❌ Error en compra</b>\n\n<i>{resultado['msg']}</i>"
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def comprar_nft_gargola_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item = {"tipo": "nft", "nombre": "Gargola-NFT", "precio": 1.0}
    resultado = await procesar_compra_item(user_id, item)
    if resultado["ok"]:
        mensaje = (
            "<b>✅ ¡Compra exitosa!</b>\n\n"
            "Has adquirido el <b>🦇 Gargola-NFT</b>\n\n"
            "<b>💰 Información:</b>\n"
            "• Precio pagado: 1.0 TON\n"
            "• Ganancia diaria: 0.025 TON\n"
            "• Duración: 365 días\n\n"
            "Tu NFT comenzará a generar ganancias automáticamente.</i>"
        )
    else:
        mensaje = resultado["msg"]
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

async def comprar_nft_ghost_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item = {"tipo": "nft", "nombre": "Ghost-NFT", "precio": 3.5}
    resultado = await procesar_compra_item(user_id, item)
    if resultado["ok"]:
        mensaje = (
            "<b>✅ ¡Compra exitosa!</b>\n\n"
            "Has adquirido el <b>👻 Ghost-NFT</b>\n\n"
            "<b>💰 Información:</b>\n"
            "• Precio pagado: 3.5 TON\n"
            "• Ganancia diaria: 0.2 TON\n"
            "• Duración: 30 días\n"
            "• ROI total: 6.0 TON\n"
            "• ROI: 171%\n\n"
            "Tu NFT comenzará a generar ganancias automáticamente.</i>"
        )
    else:
        mensaje = resultado["msg"]
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer() 

# Handler para el botón de menú '‹ Back' desde NFTs
async def back_from_nfts_handler(message: types.Message):
    # Regresa al menú de la tienda
    from modules.tienda import tienda_handler
    await tienda_handler(message)

def register_nfts_handlers(dp):
    dp.message.register(back_from_nfts_handler, lambda m: m.text == "‹ Back") 