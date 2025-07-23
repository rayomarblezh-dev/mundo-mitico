from aiogram import types
from modules.commands import mostrar_promo_paquete_bienvenida
 
async def explorar_handler(message: types.Message):
    await message.answer(
        "<b>🌍 Explorar</b>\n\n<i>Próximamente podrás explorar el mundo, descubrir criaturas, tesoros y eventos especiales.</i>",
        parse_mode="HTML"
    )
    await mostrar_promo_paquete_bienvenida(message, message.from_user.id) 