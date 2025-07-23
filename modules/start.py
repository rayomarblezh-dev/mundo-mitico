from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import agregar_referido
# Quitar la importación global de mostrar_promo_paquete_bienvenida
import datetime

async def start_handler(message: types.Message):
    # Importación local para evitar import circular
    from modules.commands import mostrar_promo_paquete_bienvenida
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
            "activo": True,
            "captcha": {"verificado": False, "codigo": None, "progreso": ""}
        })
        usuario = await usuarios_col.find_one({"user_id": user_id})
    # Si el usuario no ha pasado el captcha, mostrarlo y salir
    captcha = usuario.get("captcha", {"verificado": False, "codigo": None, "progreso": ""})
    if not captcha.get("verificado"):
        from modules.captcha import generar_captcha_qr, generar_teclado_captcha
        import os
        # Generar QR si no existe
        if not captcha.get("codigo"):
            path_qr, numeros = generar_captcha_qr()
            await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.codigo": numeros, "captcha.progreso": ""}})
            with open(path_qr, 'rb') as photo:
                await message.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
            return
        # Si ya hay código, mostrar QR existente
        codigo = captcha.get('codigo')
        path_qr = os.path.join('images', f'captcha_{codigo}.png')
        if os.path.exists(path_qr):
            from modules.captcha import generar_teclado_captcha
            with open(path_qr, 'rb') as photo:
                await message.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
            return

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

