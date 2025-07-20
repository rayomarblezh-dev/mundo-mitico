from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def heroe_kael_umbros_handler(callback: types.CallbackQuery):
    """Handler para el héroe Kael Umbros"""
    mensaje = (
        "<i><b>🐺 Kael Umbros, el Lobo del Silencio</b>\n\n"
        "En lo más profundo del Valle Sombrío, donde la luz apenas se atreve a posar y los árboles murmuran leyendas olvidadas, reina Kael Umbros, el último descendiente de los lobos sentientes. Coronado con un oro antiguo y una gema azul como el hielo que duerme en las cavernas ocultas, Kael no solo es rey, sino custodio de un poder ancestral que emana de los vientos del valle.\n\n"
        "<b>⚔️ Habilidades:</b>\n"
        "• Tajo de Silencio - Espada principal imbuida con voluntad ancestral\n"
        "• Diente de Penumbra - Daga capaz de cortar recuerdos\n"
        "• Equilibrio entre furia y paz - Símbolo de las dos espadas cruzadas\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 5 TON\n"
        "• Ganancia diaria: 0.15 TON\n"
        "• Duración: 60 días\n"
        "• ROI total: 9 TON (180%)\n\n"
        "Bajo su reinado, el Valle Sombrío se ha convertido en una tierra donde las criaturas olvidadas encuentran refugio.</i>"
    )
    
    # Crear botón de compra
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 5 TON", callback_data="comprar_kael_umbros")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def heroe_malrith_handler(callback: types.CallbackQuery):
    """Handler para el héroe Malrith el Eclipsado"""
    mensaje = (
        "<i><b>🕯️ Malrith el Eclipsado</b>\n\n"
        "Desde las profundidades más antiguas de la Cripta Silente, donde el eco de los cánticos prohibidos aún resuena entre los pilares corroídos, surgió Malrith, un ser devorado por las sombras pero jamás vencido. Su armadura, esculpida con los huesos de traidores y profetas caídos, resplandece con una oscuridad que parece absorber la luz misma.\n\n"
        "<b>⚔️ Habilidades:</b>\n"
        "• Sombrafinal - Espada templada en el río del olvido\n"
        "• Oráculo Nocturno - Gema que contiene el saber prohibido\n"
        "• Manifestación del miedo ancestral - Poder sobre las sombras\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1 TON\n"
        "• Ganancia diaria: 0.08 TON\n"
        "• Duración: 30 días\n"
        "• ROI total: 2.4 TON (140%)\n\n"
        "Malrith no busca conquistas típicas —él desea silenciar la memoria del mundo y cubrir cada amanecer con el manto eterno del crepúsculo.</i>"
    )
    
    # Crear botón de compra
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1 TON", callback_data="comprar_malrith")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()
