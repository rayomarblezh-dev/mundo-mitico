from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import os
from utils.database import usuario_tiene_nft, comprar_nft, obtener_nft_usuario

async def nfts_handler(callback: types.CallbackQuery):
    """Handler para mostrar la sección de NFTs"""
    mensaje = (
        "<i><b>🎨 NFTs</b>\n\n"
        "Los NFTs son colecciones únicas y limitadas de arte digital.\n\n"
        "<blockquote expandable>Cada NFT tiene características especiales y puede generar ganancias diarias en TON.</blockquote>\n\n"
        "<b>⚠️ Importante:</b> Solo puedes comprar <b>1 NFT</b> por usuario.\n\n"
        "<b>Selecciona un NFT para ver sus detalles y precio.</b></i>"
    )
    nfts_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🦎 Moguri-NFT", callback_data="nft_moguri"),
         InlineKeyboardButton(text="🗿 Gargola-NFT", callback_data="nft_gargola")],
        [InlineKeyboardButton(text="👻 Ghost-NFT", callback_data="nft_ghost")],
        [InlineKeyboardButton(text="🔙 Volver Atrás", callback_data="tienda_volver")]
    ])
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=nfts_keyboard)
    await callback.answer()

async def nft_moguri_handler(callback: types.CallbackQuery):
    """Handler para el NFT Moguri (común)"""
    mensaje = (
        "<i><b>🦎 Moguri-NFT (Común)</b>\n\n"
        "Un NFT misterioso con poderes ancestrales que genera ganancias diarias.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.5 TON\n"
        "• Ganancia diaria: 0.01 TON\n"
        "• Duración: 100 días\n"
        "• ROI total: 1.0 TON\n"
        "• ROI: 100%\n\n"
        "<b>🎨 Características:</b>\n"
        "— NFT de rareza común\n"
        "— Generación estable de ganancias\n"
        "— Duración media de 100 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.5 TON", callback_data="comprar_nft_moguri")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
    ])
    
    # Enviar imagen con caption y botones
    image_path = os.path.join("images", "moguri.jpg")
    photo = FSInputFile(image_path)
    await callback.message.answer_photo(photo, caption=mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    
    await callback.answer()

async def nft_gargola_handler(callback: types.CallbackQuery):
    """Handler para el NFT Gargola (común)"""
    mensaje = (
        "<i><b>🗿 Gargola-NFT (Común)</b>\n\n"
        "Un NFT protector con energía mágica que ofrece ganancias superiores.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1.0 TON\n"
        "• Ganancia diaria: 0.025 TON\n"
        "• Duración: 365 días\n"
        "• ROI total: 9.125 TON\n"
        "• ROI: 812.5%\n\n"
        "<b>🎨 Características:</b>\n"
        "— NFT de rareza común\n"
        "— Ganancia diaria superior\n"
        "— Duración extendida de 365 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1.0 TON", callback_data="comprar_nft_gargola")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
    ])
    
    # Enviar imagen con caption y botones
    image_path = os.path.join("images", "gargola.jpg")
    photo = FSInputFile(image_path)
    await callback.message.answer_photo(photo, caption=mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    
    await callback.answer()

async def nft_ghost_handler(callback: types.CallbackQuery):
    """Handler para el NFT Ghost (raro)"""
    mensaje = (
        "<i><b>👻 Ghost-NFT (Raro)</b>\n\n"
        "Un NFT etéreo de rareza superior con poderes sobrenaturales.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 3.5 TON\n"
        "• Ganancia diaria: 0.15 TON\n"
        "• Duración: 50 días\n"
        "• ROI total: 7.5 TON\n"
        "• ROI: 114.3%\n\n"
        "<b>🎨 Características:</b>\n"
        "— NFT de rareza rara\n"
        "— Ganancia diaria muy alta\n"
        "— Duración corta pero intensa</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 3.5 TON", callback_data="comprar_nft_ghost")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
    ])
    
    # Enviar imagen con caption y botones
    image_path = os.path.join("images", "ghost.jpg")
    photo = FSInputFile(image_path)
    await callback.message.answer_photo(photo, caption=mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    
    await callback.answer()

# Handlers para compra de NFTs
async def comprar_nft_moguri_handler(callback: types.CallbackQuery):
    """Handler para comprar NFT Moguri"""
    user_id = callback.from_user.id
    
    # Verificar si ya tiene un NFT
    if await usuario_tiene_nft(user_id):
        nft_actual = await obtener_nft_usuario(user_id)
        mensaje = (
            f"<b>❌ Ya tienes un NFT</b>\n\n"
            f"Ya posees el NFT: <b>{nft_actual['nft_tipo']}</b>\n"
            f"Solo puedes tener 1 NFT a la vez.\n\n"
            f"<i>Si deseas cambiar tu NFT, contacta al soporte.</i>"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
        return
    
    # Procesar compra
    try:
        await comprar_nft(user_id, "Moguri-NFT", 0.5)
        mensaje = (
            "<b>🎉 ¡Compra exitosa!</b>\n\n"
            "Has adquirido el <b>🦎 Moguri-NFT</b>\n\n"
            "<b>💰 Información:</b>\n"
            "• Precio pagado: 0.5 TON\n"
            "• Ganancia diaria: 0.01 TON\n"
            "• Duración: 100 días\n\n"
            "<i>Tu NFT comenzará a generar ganancias automáticamente.</i>"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver a la Tienda", callback_data="tienda_volver")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        mensaje = "<b>❌ Error en la compra</b>\n\nHubo un problema al procesar tu compra. Intenta nuevamente."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()

async def comprar_nft_gargola_handler(callback: types.CallbackQuery):
    """Handler para comprar NFT Gargola"""
    user_id = callback.from_user.id
    
    # Verificar si ya tiene un NFT
    if await usuario_tiene_nft(user_id):
        nft_actual = await obtener_nft_usuario(user_id)
        mensaje = (
            f"<b>❌ Ya tienes un NFT</b>\n\n"
            f"Ya posees el NFT: <b>{nft_actual['nft_tipo']}</b>\n"
            f"Solo puedes tener 1 NFT a la vez.\n\n"
            f"<i>Si deseas cambiar tu NFT, contacta al soporte.</i>"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
        return
    
    # Procesar compra
    try:
        await comprar_nft(user_id, "Gargola-NFT", 1.0)
        mensaje = (
            "<b>🎉 ¡Compra exitosa!</b>\n\n"
            "Has adquirido el <b>🗿 Gargola-NFT</b>\n\n"
            "<b>💰 Información:</b>\n"
            "• Precio pagado: 1.0 TON\n"
            "• Ganancia diaria: 0.025 TON\n"
            "• Duración: 365 días\n\n"
            "<i>Tu NFT comenzará a generar ganancias automáticamente.</i>"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver a la Tienda", callback_data="tienda_volver")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        mensaje = "<b>❌ Error en la compra</b>\n\nHubo un problema al procesar tu compra. Intenta nuevamente."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()

async def comprar_nft_ghost_handler(callback: types.CallbackQuery):
    """Handler para comprar NFT Ghost"""
    user_id = callback.from_user.id
    
    # Verificar si ya tiene un NFT
    if await usuario_tiene_nft(user_id):
        nft_actual = await obtener_nft_usuario(user_id)
        mensaje = (
            f"<b>❌ Ya tienes un NFT</b>\n\n"
            f"Ya posees el NFT: <b>{nft_actual['nft_tipo']}</b>\n"
            f"Solo puedes tener 1 NFT a la vez.\n\n"
            f"<i>Si deseas cambiar tu NFT, contacta al soporte.</i>"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
        return
    
    # Procesar compra
    try:
        await comprar_nft(user_id, "Ghost-NFT", 3.5)
        mensaje = (
            "<b>🎉 ¡Compra exitosa!</b>\n\n"
            "Has adquirido el <b>👻 Ghost-NFT</b>\n\n"
            "<b>💰 Información:</b>\n"
            "• Precio pagado: 3.5 TON\n"
            "• Ganancia diaria: 0.15 TON\n"
            "• Duración: 50 días\n\n"
            "<i>Tu NFT comenzará a generar ganancias automáticamente.</i>"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver a la Tienda", callback_data="tienda_volver")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        mensaje = "<b>❌ Error en la compra</b>\n\nHubo un problema al procesar tu compra. Intenta nuevamente."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")]
        ])
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer() 