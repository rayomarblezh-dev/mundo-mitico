from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

async def wallet_retirar_handler(callback: types.CallbackQuery):
    mensaje = (
        "<i><b>📤 Retirar\n\n"
        "Red disponible para retiros:</b>\n\n"
        "— TON\n\n"
        "<b>⚠️ Mínimo:</b> 1.1 TON\n\n"
        "<b>Ingresa la cantidad que deseas retirar.</b></i>"
    )
    retirar_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Retirar", callback_data="retirar_iniciar")]
    ])
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=retirar_keyboard)
    await callback.answer() 