from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import agregar_referido

async def start_handler(message: types.Message):
    # Manejo de referidos
    args = None
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            args = parts[1]
    if args:
        if args.startswith("ref_"):
            try:
                referidor_id = int(args.replace("ref_", ""))
                user_id = message.from_user.id
                if referidor_id != user_id:
                    # Intentar registrar el referido (ignorar si ya existe)
                    try:
                        await agregar_referido(referidor_id, user_id)
                    except Exception:
                        pass
            except Exception:
                pass

    welcome_text = (
        "<i><b>👋 ¡Bienvenido a Mundo Mítico!\n\n"
        "Sumérgete en un universo épico donde las criaturas legendarias aguardan ser descubiertas. En este mundo de aventuras, podrás:</b>\n"
        "<blockquote expandable>— <b>Cazar Criaturas</b> - Encuentra y captura bestias míticas\n"
        "— <b>Expediciones</b>  - Explora territorios desconocidos\n"
        "— <b>Combates Épicos</b>  - Enfréntate a desafíos legendarios\n"
        "— <b>Invertir TON</b>  - Gestiona tu economía en el mundo mítico\n"
        "— <b>Generar Ganancias</b>  - Atrapa criaturas y compra héroes que producen diariamente</blockquote>\n"
        "<b>¡Tu aventura comienza ahora! Elige tu camino y forja tu leyenda en este mundo.</b></i>\n\n"
    )
    
    # Crear botones de menú
    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌍\nExplorar")],
            [KeyboardButton(text="🛍\nTienda"), KeyboardButton(text="🧳\nInventario")],
            [KeyboardButton(text="👛\nWallet"), KeyboardButton(text="👥\nReferidos")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    # Crear botones inline
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📣 Canal", url="https://t.me/MundoMitico"),
            InlineKeyboardButton(text="📮 Soporte", callback_data="support")   
        ],
        [
            InlineKeyboardButton(text="📕 Tutoriales", callback_data="tutorials")
        ]
    ])
    
    # Enviar mensaje con botones inline
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=inline_keyboard)
    
    # Enviar botones de menú por separado
    await message.answer("<i><b>Menú Principal</b></i>", reply_markup=menu_keyboard, parse_mode="HTML")

