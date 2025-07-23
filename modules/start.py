from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import agregar_referido
# Quitar la importación global de mostrar_promo_paquete_bienvenida

async def start_handler(message: types.Message):
    # Importación local para evitar import circular
    from modules.commands import mostrar_promo_paquete_bienvenida
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
        "👋 ¡Bienvenido a Mundo Mítico!\n\n"
        "<i>Sumérgete en un universo épico donde las criaturas legendarias aguardan ser descubiertas. En este mundo de aventuras, podrás:\n"
        "<blockquote expandable>— <b>Cazar Criaturas</b> - Encuentra y captura bestias míticas\n"
        "— <b>Expediciones</b>  - Explora territorios desconocidos\n"
        "— <b>Combates Épicos</b>  - Enfréntate a desafíos legendarios\n"
        "— <b>Invertir TON</b>  - Gestiona tu economía en el mundo mítico\n"
        "— <b>Generar Ganancias</b>  - Atrapa criaturas y compra héroes que producen diariamente</blockquote></i>\n"
        "<b>🤩 ¡Tu aventura comienza ahora! Elige tu camino y forja tu leyenda en este mundo.</b>\n\n"
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
            InlineKeyboardButton(text="📮 Soporte", url="http://t.me/wolfpromot")   
        ],
        [
            InlineKeyboardButton(text="📕 Guia", callback_data="guia")
        ]
    ])
    
    # Enviar mensaje con botones inline
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=inline_keyboard)
    
    # Enviar botones de menú por separado
    await message.answer("🏠 <b>Menú Principal</b>", reply_markup=menu_keyboard, parse_mode="HTML")

    # Al final del handler, mostrar la promo si aplica
    await mostrar_promo_paquete_bienvenida(message, message.from_user.id)

