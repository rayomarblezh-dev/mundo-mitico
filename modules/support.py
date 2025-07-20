from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def support_callback_handler(callback: types.CallbackQuery):
    mensaje = (
        "<b>📮 Soporte</b>\n\n"
        "¿Tienes dudas o necesitas ayuda?"
    )
    soporte_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Admin", url="https://t.me/wolfpromot")]
    ])
    await callback.message.answer(mensaje, reply_markup=soporte_keyboard, parse_mode="HTML")
    await callback.answer()