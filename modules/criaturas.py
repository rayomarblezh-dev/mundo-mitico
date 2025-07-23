from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def criatura_hada_handler(callback: types.CallbackQuery):
    """Handler para la criatura Hada"""
    mensaje = (
        "<b>🧚‍♀️ Hada</b>\n\n"
        "<i>Seres mágicos de los bosques encantados que traen buena fortuna y protección a sus dueños.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.10 TON\n"
        "• Producción diaria: 1.00%\n"
        "• Ganancia diaria: 0.0010 TON\n"
        "• ROI: 70%\n"
        "• ROI total: 0.17 TON\n"
        "• Tiempo de vida: 100 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.10 TON", callback_data="comprar_hada")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_elfo_handler(callback: types.CallbackQuery):
    """Handler para la criatura Elfo"""
    mensaje = (
        "<b>🧙‍♂️ Elfo</b>\n\n"
        "<i>Guardianes ancestrales de la sabiduría mágica, conocedores de los secretos más profundos de la naturaleza.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.11 TON\n"
        "• Producción diaria: 1.30%\n"
        "• Ganancia diaria: 0.00143 TON\n"
        "• ROI: 75%\n"
        "• ROI total: 0.1925 TON\n"
        "• Tiempo de vida: ~77 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.11 TON", callback_data="comprar_elfo")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_dragon_handler(callback: types.CallbackQuery):
    """Handler para la criatura Dragón"""
    mensaje = (
        "<b>🐉 Dragón</b>\n\n"
        "<i>Majestuosas criaturas de fuego y poder, guardianes de tesoros legendarios y maestros del cielo.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.20 TON\n"
        "• Producción diaria: 1.45%\n"
        "• Ganancia diaria: 0.0029 TON\n"
        "• ROI: 80%\n"
        "• ROI total: 0.36 TON\n"
        "• Tiempo de vida: ~69 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.20 TON", callback_data="comprar_dragon")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_orco_handler(callback: types.CallbackQuery):
    """Handler para la criatura Orco"""
    mensaje = (
        "<b>👹 Orco</b>\n\n"
        "<i>Guerreros feroces de las montañas oscuras, conocidos por su fuerza bruta y resistencia en batalla.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.22 TON\n"
        "• Producción diaria: 1.50%\n"
        "• Ganancia diaria: 0.0033 TON\n"
        "• ROI: 90%\n"
        "• ROI total: 0.418 TON\n"
        "• Tiempo de vida: ~67 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.22 TON", callback_data="comprar_orco")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_gremnli_handler(callback: types.CallbackQuery):
    """Handler para la criatura Gremnli"""
    mensaje = (
        "<b>👺 Gremnli</b>\n\n"
        "<i>Tramposos astutos de las cavernas subterráneas, maestros del engaño y la supervivencia.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.25 TON\n"
        "• Producción diaria: 1.55%\n"
        "• Ganancia diaria: 0.003875 TON\n"
        "• ROI: 99%\n"
        "• ROI total: 0.4975 TON\n"
        "• Tiempo de vida: ~65 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.25 TON", callback_data="comprar_gremnli")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_unicornio_handler(callback: types.CallbackQuery):
    """Handler para la criatura Unicornio"""
    mensaje = (
        "<b>🦄 Unicornio</b>\n\n"
        "<i>Criaturas puras y mágicas, símbolos de pureza y poder curativo, guardianes de la luz.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.30 TON\n"
        "• Producción diaria: 1.60%\n"
        "• Ganancia diaria: 0.0048 TON\n"
        "• ROI: 110%\n"
        "• ROI total: 0.63 TON\n"
        "• Tiempo de vida: ~63 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.30 TON", callback_data="comprar_unicornio")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_genio_handler(callback: types.CallbackQuery):
    """Handler para la criatura Genio"""
    mensaje = (
        "<b>🧞 Genio</b>\n\n"
        "<i>Seres de poder ilimitado, capaces de conceder deseos y manipular la realidad misma.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.40 TON\n"
        "• Producción diaria: 2.00%\n"
        "• Ganancia diaria: 0.0080 TON\n"
        "• ROI: 150%\n"
        "• ROI total: 1.00 TON\n"
        "• Tiempo de vida: 50 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.40 TON", callback_data="comprar_genio")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_kraken_handler(callback: types.CallbackQuery):
    """Handler para la criatura Kraken"""
    mensaje = (
        "<b>👾 Kraken</b>\n\n"
        "<i>Titanes del océano profundo, criaturas colosales que gobiernan las aguas más oscuras.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1.20 TON\n"
        "• Producción diaria: 3.50%\n"
        "• Ganancia diaria: 0.0420 TON\n"
        "• ROI: 210%\n"
        "• ROI total: 3.72 TON\n"
        "• Tiempo de vida: ~29 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1.20 TON", callback_data="comprar_kraken")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_licantropo_handler(callback: types.CallbackQuery):
    """Handler para la criatura Licántropo"""
    mensaje = (
        "<b>🐺 Licántropo</b>\n\n"
        "<i>Guerreros que se transforman bajo la luna llena, combinando la ferocidad del lobo con la inteligencia humana.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1.00 TON\n"
        "• Producción diaria: 3.00%\n"
        "• Ganancia diaria: 0.0300 TON\n"
        "• ROI: 200%\n"
        "• ROI total: 3.00 TON\n"
        "• Tiempo de vida: ~34 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1.00 TON", callback_data="comprar_licantropo")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()
