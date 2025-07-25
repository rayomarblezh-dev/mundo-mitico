from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

async def tienda_handler(message: types.Message):
    mensaje = (
        "<b>🛍 Tienda</b>\n\n"
        "Bienvenido a la tienda de <b>Mundo Mítico</b>.\n\n"
        "<blockquote>Aquí puedes adquirir criaturas míticas y NFTs únicos.\nAmbos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "Selecciona una categoría para ver los productos disponibles y obtener información detallada sobre cada uno."
    )
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🐾 Criaturas", callback_data="tienda_criaturas"),
            InlineKeyboardButton(text="🎨 NFTs", callback_data="tienda_nfts")
        ],
        [InlineKeyboardButton(text="🔥 Promociones", callback_data="tienda_promos")]
    ])
    await message.answer(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)

async def tienda_criaturas_handler(callback: types.CallbackQuery):
    mensaje = (
        "<b>🐾 Criaturas</b>\n\n"
        "Las criaturas míticas son seres poderosos que puedes capturar y entrenar.\n\n"
        "<blockquote>Cada criatura tiene habilidades especiales y puede ayudarte en combates.</blockquote>\n\n"
        "Selecciona una criatura para ver sus detalles y precio."
    )
    criaturas_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🧚‍♀️ Hada", callback_data="criatura_hada"),
            InlineKeyboardButton(text="🧙‍♂️ Mago", callback_data="criatura_mago")
        ],
        [
            InlineKeyboardButton(text="🐉 Dragón", callback_data="criatura_dragon"),
            InlineKeyboardButton(text="👹 Orco", callback_data="criatura_orco")
        ],
        [
            InlineKeyboardButton(text="👺 Gremnli", callback_data="criatura_gremnli"),
            InlineKeyboardButton(text="🦄 Unicornio", callback_data="criatura_unicornio")
        ],
        [
            InlineKeyboardButton(text="🧞 Genio", callback_data="criatura_genio"),
            InlineKeyboardButton(text="👾 Kraken", callback_data="criatura_kraken")
        ],
        [InlineKeyboardButton(text="🐺 Licántropo", callback_data="criatura_licantropo")],
    ])
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=criaturas_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=criaturas_keyboard)
    await callback.answer()

async def tienda_volver_handler(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    mensaje = (
        "<b>🛍 Tienda</b>\n\n"
        "Bienvenido a la tienda de <b>Mundo Mítico</b>.\n\n"
        "<blockquote>Aquí puedes adquirir criaturas míticas y NFTs únicos.\nAmbos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "Selecciona una categoría para ver los productos disponibles y obtener información detallada sobre cada uno."
    )
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🐾 Criaturas", callback_data="tienda_criaturas"),
            InlineKeyboardButton(text="🎨 NFTs", callback_data="tienda_nfts")
        ],
        [InlineKeyboardButton(text="🔥 Promociones", callback_data="tienda_promos")]
    ])
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)
    await callback.answer()

from aiogram.types import CallbackQuery
from utils.database import es_elegible_paquete_bienvenida, procesar_compra_item

async def tienda_promos_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await es_elegible_paquete_bienvenida(user_id):
        promo_text = (
            '<b>💎 ¡Paquete de bienvenida!</b>\n'
            '7 🧚 Hadas, 3 🧙 Magos, 1 🐺 Licántropo por solo <b>1.5 TON</b>.\n'
            '<i>Solo por 15 días desde tu registro.</i>'
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Comprar", callback_data="comprar_paquete_bienvenida")]
            ]
        )
        try:
            await callback.message.edit_text(promo_text, parse_mode="HTML", reply_markup=keyboard)
        except Exception:
            await callback.message.answer(promo_text, parse_mode="HTML", reply_markup=keyboard)
    else:
        texto_no_promo = "Actualmente no hay promociones disponibles para ti."
        try:
            await callback.message.edit_text(texto_no_promo, parse_mode="HTML")
        except Exception:
            await callback.message.answer(texto_no_promo, parse_mode="HTML")
    await callback.answer()

async def comprar_paquete_bienvenida_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    item = {"tipo": "promo", "nombre": "paquete_bienvenida", "precio": 1.5}
    try:
        resultado = await procesar_compra_item(user_id, item)
        if resultado.get("ok"):
            mensaje = (
                "<b>✅ Compra Exitosa</b>\n\n"
                "<i>🎉 ¡Has comprado el paquete de bienvenida! Las criaturas han sido añadidas a tu inventario.</i>"
            )
        else:
            mensaje = (
                f"<b>❌ Error en Compra</b>\n\n"
                f"<i>{resultado.get('msg', 'Ha ocurrido un error inesperado.')}</i>"
            )
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML")
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML")
    except Exception as e:
        mensaje = (
            "<b>❌ Error en Compra</b>\n\n"
            "<i>Ha ocurrido un error inesperado al procesar tu compra. Por favor, intenta nuevamente más tarde.</i>"
        )
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML")
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()

# Handler para el botón de menú '‹ Back' desde criaturas
async def back_from_criaturas_handler(message: types.Message):
    # Regresa al menú de la tienda
    mensaje = (
        "<b>🛍 Tienda</b>\n\n"
        "Bienvenido a la tienda de <b>Mundo Mítico</b>.\n\n"
        "<blockquote>Aquí puedes adquirir criaturas míticas y NFTs únicos.\nAmbos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "Selecciona una categoría para ver los productos disponibles y obtener información detallada sobre cada uno."
    )
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🐾 Criaturas", callback_data="tienda_criaturas"),
            InlineKeyboardButton(text="🎨 NFTs", callback_data="tienda_nfts")
        ],
        [InlineKeyboardButton(text="🔥 Promociones", callback_data="tienda_promos")]
    ])
    # Oculta el teclado reply
    await message.answer(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)

# Registrar los handlers en el router (dispatcher)
def register_tienda_handlers(dp):
    dp.callback_query.register(
        tienda_promos_handler, 
        lambda c: c.data == "tienda_promos"
    )
    dp.callback_query.register(
        comprar_paquete_bienvenida_handler, 
        lambda c: c.data == "comprar_paquete_bienvenida"
    )
    # Handler para el botón de menú '‹ Back' desde criaturas
    dp.message.register(back_from_criaturas_handler, lambda m: m.text == "‹ Volver")