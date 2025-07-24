from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from utils.database import agregar_referido
import datetime

async def start_handler(message: types.Message):
    # Importación local para evitar import circular
    from utils.database import usuarios_col
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    # Crear usuario si no existe y asegurar campo captcha
    usuario = await usuarios_col.find_one({"user_id": user_id})
    if not usuario:
        await usuarios_col.insert_one({
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "balance": 0.0,
            "fecha_registro": datetime.datetime.now(),
            "activo": True
        })
        usuario = await usuarios_col.find_one({"user_id": user_id})

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
                if referidor_id != user_id:
                    # Intentar registrar el referido (ignorar si ya existe)
                    await agregar_referido(referidor_id, user_id)
            except ValueError:
                pass  # El argumento no es un número válido
            except Exception as e:
                print(f"Error al agregar referido: {e}")

    welcome_text = (
        "🌍 ¡Bienvenido a Mundo Mítico!\n\n"
        "<i>Sumérgete en un universo épico donde las criaturas legendarias aguardan ser descubiertas. En este mundo de aventuras, podrás:\n"
        "<blockquote expandable>— <b>Cazar Criaturas</b> - Encuentra y captura bestias míticas\n"
        "— <b>Expediciones</b>  - Explora territorios desconocidos\n"
        "— <b>Combates Épicos</b>  - Enfréntate a desafíos legendarios\n"
        "— <b>Invertir TON</b>  - Gestiona tu economía en el mundo mítico\n"
        "— <b>Generar Ganancias</b>  - Atrapa criaturas y compra héroes que producen diariamente</blockquote></i>\n"
        "<b>¡Tu aventura comienza ahora! Elige tu camino y forja tu leyenda en este mundo.</b>\n\n"
        "<b>Accesos rápidos:</b>"
    )
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌍\nExplorar")],
            [KeyboardButton(text="🛍\nTienda"), KeyboardButton(text="🧳\nInventario")],
            [KeyboardButton(text="👛\nWallet"), KeyboardButton(text="👥\nReferidos")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    copy_button = CopyTextButton(text="ABC123")

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📣 Canal", url="https://t.me/MundoMitico"),
        InlineKeyboardButton(text="📮 Soporte", url="http://t.me/wolfpromot")   
    ],
    [InlineKeyboardButton(text="Copiar"[copy_button]) ] # Añadido como fila separada
])

    # Enviar un solo mensaje con ambos teclados (reply y inline)
    await message.reply("Hola", reply_markup=reply_kb)
    await message.answer(welcome_text, reply_markup=inline_kb, parse_mode="HTML")
    
    
