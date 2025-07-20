from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def nfts_handler(callback: types.CallbackQuery):
    mensaje = (
        "<i><b>🧊 NFT Hielo</b>\n"
        "Precio: 19.99 TON\n"
        "Ganancia diaria: 0.09 TON\n"
        "Tiempo: 365 días\n\n"
        "<b>🏅 NFT Oro</b>\n"
        "Precio: 7 TON\n"
        "Ganancia diaria: 0.2 TON\n"
        "Tiempo: 45 días\n\n"
        "<b>🌑 NFT Oscuro</b>\n"
        "Precio: 10 TON\n"
        "Ganancia diaria: 0.05 TON\n"
        "Duración: Ilimitado</i>"
    )
    nfts_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Hielo", callback_data="comprar_nft_hielo")],
        [InlineKeyboardButton(text="Oro", callback_data="comprar_nft_oro")],
        [InlineKeyboardButton(text="Oscuro", callback_data="comprar_nft_oscuro")],
        [InlineKeyboardButton(text="🔙 Volver Atrás", callback_data="tienda_volver")]
    ])
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=nfts_keyboard)
    await callback.answer()

async def comprar_nft_hielo_handler(callback: types.CallbackQuery):
    await callback.message.answer("La compra de NFT Hielo estará disponible próximamente.")
    await callback.answer()

async def comprar_nft_oro_handler(callback: types.CallbackQuery):
    await callback.message.answer("La compra de NFT Oro estará disponible próximamente.")
    await callback.answer()

async def comprar_nft_oscuro_handler(callback: types.CallbackQuery):
    await callback.message.answer("La compra de NFT Oscuro estará disponible próximamente.")
    await callback.answer()
