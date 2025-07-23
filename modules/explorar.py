from aiogram import types
# Quitar la importación global de mostrar_promo_paquete_bienvenida
 
async def explorar_handler(message: types.Message):
    from modules.commands import mostrar_promo_paquete_bienvenida
    await message.answer(
        "<b>🌍 Explorar</b>\n\n<i>Próximamente podrás explorar el mundo, descubrir criaturas, tesoros y eventos especiales.</i>",
        parse_mode="HTML"
    )