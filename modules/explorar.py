from aiogram import types
 
async def explorar_handler(message: types.Message):
    await message.answer(
        "<b>🌍 Explorar</b>\n\nPróximamente podrás explorar el mundo, descubrir criaturas, tesoros y eventos especiales.",
        parse_mode="HTML"
    ) 