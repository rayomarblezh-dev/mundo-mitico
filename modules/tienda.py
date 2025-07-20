from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def tienda_handler(message: types.Message):
    mensaje = (
        "<i><b>🛍 Tienda</b>\n\n"
        "Bienvenido a la tienda de <b>Mundo Mítico.</b>\n\n"
        "<blockquote expandable>Aquí puedes adquirir héroes y criaturas\n— Ambos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "<b>Selecciona una categoría — verás los productos disponibles y obtendrás información detallada sobre cada uno.</b></i>"
    )
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Héroes", callback_data="tienda_heroes"),
         InlineKeyboardButton(text="Criaturas", callback_data="tienda_criaturas")],
        [InlineKeyboardButton(text="NFTs", callback_data="tienda_nfts")]
    ])
    await message.answer(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)

async def tienda_heroes_handler(callback: types.CallbackQuery):
    mensaje = (
        "<i><b>⚔️ Héroes</b>\n\n"
        "Los héroes son guerreros legendarios que te ayudarán en tu aventura.\n\n"
        "<blockquote expandable>Cada héroe tiene habilidades únicas y puede generar TON diariamente.</blockquote>\n\n"
        "<b>Selecciona un héroe para ver sus detalles y precio.</b></i>"
    )
    heroes_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐺 Kael Umbros", callback_data="heroe_kael_umbros")],
        [InlineKeyboardButton(text="🕯️ Malrith el Eclipsado", callback_data="heroe_malrith")],
        [InlineKeyboardButton(text="🔙 Volver Atrás", callback_data="tienda_volver")]
    ])
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=heroes_keyboard)
    await callback.answer()

async def tienda_criaturas_handler(callback: types.CallbackQuery):
    mensaje = (
        "<i><b>🐉 Criaturas</b>\n\n"
        "Las criaturas míticas son seres poderosos que puedes capturar y entrenar.\n\n"
        "<blockquote expandable>Cada criatura tiene habilidades especiales y puede ayudarte en combates.</blockquote>\n\n"
        "<b>Selecciona una criatura para ver sus detalles y precio.</b></i>"
    )
    criaturas_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧚‍♀️ Hada", callback_data="criatura_hada"),
         InlineKeyboardButton(text="🧙‍♂️ Elfo", callback_data="criatura_elfo")],
        [InlineKeyboardButton(text="🐉 Dragón", callback_data="criatura_dragon"),
         InlineKeyboardButton(text="👹 Orco", callback_data="criatura_orco")],
        [InlineKeyboardButton(text="👺 Gremnli", callback_data="criatura_gremnli"),
         InlineKeyboardButton(text="🦄 Unicornio", callback_data="criatura_unicornio")],
        [InlineKeyboardButton(text="🧞 Genio", callback_data="criatura_genio"),
         InlineKeyboardButton(text="👾 Kraken", callback_data="criatura_kraken")],
        [InlineKeyboardButton(text="🐺 Licántropo", callback_data="criatura_licantropo")],
        [InlineKeyboardButton(text="🔙 Volver Atrás", callback_data="tienda_volver")]
    ])
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=criaturas_keyboard)
    await callback.answer()

async def tienda_volver_handler(callback: types.CallbackQuery):
    mensaje = (
        "<i><b>🛍 Tienda</b>\n\n"
        "Bienvenido a la tienda de <b>Mundo Mítico.</b>\n\n"
        "<blockquote expandable>Aquí puedes adquirir héroes y criaturas\n— Ambos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "<b>Selecciona una categoría — verás los productos disponibles y obtendrás información detallada sobre cada uno.</b></i>"
    )
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Héroes", callback_data="tienda_heroes"),
         InlineKeyboardButton(text="Criaturas", callback_data="tienda_criaturas")],
        [InlineKeyboardButton(text="NFTs", callback_data="tienda_nfts")]
    ])
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)
    await callback.answer() 