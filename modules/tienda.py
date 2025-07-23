from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from modules.commands import mostrar_promo_paquete_bienvenida

async def tienda_handler(message: types.Message):
    mensaje = (
        "<b>🛍 Tienda</b>\n\n"
        "<i>Bienvenido a la tienda de <b>Mundo Mítico.</b>\n\n"
        "<blockquote expandable>Aquí puedes adquirir criaturas míticas y NFTs únicos\n— Ambos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "<b>Selecciona una categoría — verás los productos disponibles y obtendrás información detallada sobre cada uno.</b></i>"
    )
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(text="🐾 Criaturas", callback_data="tienda_criaturas"),
          InlineKeyboardButton(text="🎨 NFTs", callback_data="tienda_nfts")]
    ])
    await message.answer(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)
    await mostrar_promo_paquete_bienvenida(message, message.from_user.id)

async def tienda_criaturas_handler(callback: types.CallbackQuery):
    mensaje = (
        "<b>🐾 Criaturas</b>\n\n"
        "<i>Las criaturas míticas son seres poderosos que puedes capturar y entrenar.\n\n"
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
    await mostrar_promo_paquete_bienvenida(callback.message, callback.from_user.id)

async def tienda_volver_handler(callback: types.CallbackQuery):
    # Eliminar el mensaje anterior si existe
    try:
        await callback.message.delete()
    except Exception:
        pass
    mensaje = (
        "<b>🛍 Tienda</b>\n\n"
        "<i>Bienvenido a la tienda de <b>Mundo Mítico.</b>\n\n"
        "<blockquote expandable>Aquí puedes adquirir criaturas míticas y NFTs únicos\n— Ambos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "<b>Selecciona una categoría — verás los productos disponibles y obtendrás información detallada sobre cada uno.</b></i>"
    )
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Criaturas", callback_data="tienda_criaturas"),
         InlineKeyboardButton(text="🎨 NFTs", callback_data="tienda_nfts")]
    ])
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)
    await callback.answer() 