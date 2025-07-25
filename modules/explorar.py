from aiogram import types

async def explorar_handler(message: types.Message):
    texto = (
        "<b>🌍 Explorar</b>\n\n"
        "<blockquote expandable>"
        "¡Muy pronto podrás embarcarte en aventuras épicas! Descubre nuevas criaturas, encuentra tesoros ocultos y participa en eventos especiales que te esperan en el mundo de Explorar. "
        "Mantente atento a las próximas actualizaciones para ser de los primeros en vivir esta experiencia."
        "</blockquote>"
    )
    await message.answer(
        texto,
        parse_mode="HTML"
    )