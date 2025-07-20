from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

async def start_handler(message: types.Message):
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

async def support_callback_handler(callback: types.CallbackQuery):
    mensaje = (
        "<b>📮 Soporte</b>\n\n"
        "¿Tienes dudas o necesitas ayuda?"
    )
    soporte_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Admin", url="https://t.me/wolfpromot")]
    ])
    await callback.message.answer(mensaje, reply_markup=soporte_keyboard, parse_mode="HTML")

async def tutorials_callback_handler(callback: types.CallbackQuery):
    cartel = (
        "⚠️ Próximamente\n\n"
    )
    await callback.answer(cartel, show_alert=True)

async def referidos_handler(message: types.Message):
    """Handler para el botón de menú Referidos"""
    user_id = message.from_user.id
    ref_link = f"https://t.me/{(await message.bot.get_me()).username}?start=ref_{user_id}"
    
    mensaje = (
        "<i><b>👥 Referidos</b>\n\n"
        "— Invita a tus amigos y gana recompensas exclusivas.\n\n"
        "— Comparte tu enlace único y ambos recibirán beneficios especiales.\n\n"
        "<b>🎁 Recompensas:</b>\n\n"
        "— Cada 10 invitaciones: 1 Hada\n\n"
        "— Cada referido que invierta: 1 Elfo\n\n"
        "<b>¡Más invitados, más recompensas!</b></i>"
    )
    
    # Crear botón de compartir
    share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Compartir", url=f"https://t.me/share/url?url={ref_link}")],
    ])
    
    await message.answer(mensaje, parse_mode="HTML", reply_markup=share_keyboard)

async def tienda_handler(message: types.Message):
    """Handler para el botón de menú Tienda"""
    mensaje = (
        "<i><b>🛍 Tienda</b>\n\n"
        "Bienvenido a la tienda de <b>Mundo Mítico.</b>\n\n"
        "<blockquote expandable>Aquí puedes adquirir héroes y criaturas\n— Ambos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "<b>Selecciona una categoría — verás los productos disponibles y obtendrás información detallada sobre cada uno.</b></i>"
    )
    
    # Crear botones de categorías
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Héroes", callback_data="tienda_heroes"),
        InlineKeyboardButton(text="Criaturas", callback_data="tienda_criaturas")]
    ])
    
    await message.answer(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)

async def wallet_handler(message: types.Message):
    """Handler para el botón de menú Wallet"""
    # Simular balance (aquí conectarías con tu base de datos)
    balance_ton = 0.0  # Reemplazar con balance real de la base de datos
    
    mensaje = (
        f"<i><b>👛 Wallet</b>\n\n"
        f"Gestiona tus fondos en <b>Mundo Mítico.</b>\n\n"
        f"<b>💰 Balance:</b> {balance_ton} TON\n\n"
        f"<blockquote expandable>Deposita para invertir en héroes y criaturas\n— Retira tus ganancias cuando lo desees</blockquote>\n\n"
        f"<b>Selecciona una opción para continuar.</b></i>"
    )
    
    # Crear botones de wallet
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Depositar", callback_data="wallet_depositar"),
        InlineKeyboardButton(text="Retirar", callback_data="wallet_retirar")]
    ])
    
    await message.answer(mensaje, parse_mode="HTML", reply_markup=wallet_keyboard)

async def wallet_depositar_handler(callback: types.CallbackQuery):
    """Handler para el botón de depositar"""
    mensaje = (
        "<i><b>📥 Depositar\n\n"
        "Redes disponibles para depositos:</b>\n\n"
        "— USDT Bep20\n"
        "— USDT TON\n"
        "— TON\n"
        "— TRX Trc20\n\n"
        "<b>⚠️ Mínimo:</b> 0.5 TON equivalente en USD\n\n"
        "<b>Selecciona la red para obtener la dirección de depósito.</b></i>"
    )
    
    # Crear botones de redes
    depositar_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="USDT Bep20", callback_data="depositar_usdt_bep20"),
        InlineKeyboardButton(text="USDT TON", callback_data="depositar_usdt_ton")],
        [InlineKeyboardButton(text="TON", callback_data="depositar_ton"),
        InlineKeyboardButton(text="TRX Trc20", callback_data="depositar_trx")]
        
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=depositar_keyboard)
    await callback.answer()

async def wallet_retirar_handler(callback: types.CallbackQuery):
    """Handler para el botón de retirar"""
    mensaje = (
        "<i><b>📤 Retirar\n\n"
        "Red disponible para retiros:</b>\n\n"
        "— TON\n\n"
        "<b>⚠️ Mínimo:</b> 1.1 TON\n\n"
        "<b>Ingresa la cantidad que deseas retirar.</b></i>"
    )
    
    # Crear botón para iniciar retiro
    retirar_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Retirar", callback_data="retirar_iniciar")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=retirar_keyboard)
    await callback.answer()

async def tienda_heroes_handler(callback: types.CallbackQuery):
    """Handler para la categoría Héroes"""
    mensaje = (
        "<i><b>⚔️ Héroes</b>\n\n"
        "Los héroes son guerreros legendarios que te ayudarán en tu aventura.\n\n"
        "<blockquote expandable>Cada héroe tiene habilidades únicas y puede generar TON diariamente.</blockquote>\n\n"
        "<b>Selecciona un héroe para ver sus detalles y precio.</b></i>"
    )
    
    # Aquí agregaremos los botones de los 4 héroes
    heroes_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐺 Kael Umbros", callback_data="heroe_kael_umbros")],
        [InlineKeyboardButton(text="🕯️ Malrith el Eclipsado", callback_data="heroe_malrith")],
        [InlineKeyboardButton(text="⬅️ Volver Atrás", callback_data="tienda_volver")]
    ])
    
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=heroes_keyboard)
    await callback.answer()

async def tienda_criaturas_handler(callback: types.CallbackQuery):
    """Handler para la categoría Criaturas"""
    mensaje = (
        "<i><b>🐉 Criaturas</b>\n\n"
        "Las criaturas míticas son seres poderosos que puedes capturar y entrenar.\n\n"
        "<blockquote expandable>Cada criatura tiene habilidades especiales y puede ayudarte en combates.</blockquote>\n\n"
        "<b>Selecciona una criatura para ver sus detalles y precio.</b></i>"
    )
    
    # Aquí agregaremos los botones de las criaturas
    criaturas_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧚‍♀️ Hada", callback_data="criatura_hada")],
        [InlineKeyboardButton(text="🧙‍♂️ Elfo", callback_data="criatura_elfo")],
        [InlineKeyboardButton(text="🐉 Dragón", callback_data="criatura_dragon")],
        [InlineKeyboardButton(text="👹 Orco", callback_data="criatura_orco")],
        [InlineKeyboardButton(text="👺 Gremnli", callback_data="criatura_gremnli")],
        [InlineKeyboardButton(text="🦄 Unicornio", callback_data="criatura_unicornio")],
        [InlineKeyboardButton(text="🧞 Genio", callback_data="criatura_genio")],
        [InlineKeyboardButton(text="👾 Kraken", callback_data="criatura_kraken")],
        [InlineKeyboardButton(text="🐺 Licántropo", callback_data="criatura_licantropo")],
        [InlineKeyboardButton(text="⬅️ Volver Atrás", callback_data="tienda_volver")]
    ])
    
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=criaturas_keyboard)
    await callback.answer()

async def heroe_kael_umbros_handler(callback: types.CallbackQuery):
    """Handler para el héroe Kael Umbros"""
    mensaje = (
        "<i><b>🐺 Kael Umbros, el Lobo del Silencio</b>\n\n"
        "En lo más profundo del Valle Sombrío, donde la luz apenas se atreve a posar y los árboles murmuran leyendas olvidadas, reina Kael Umbros, el último descendiente de los lobos sentientes. Coronado con un oro antiguo y una gema azul como el hielo que duerme en las cavernas ocultas, Kael no solo es rey, sino custodio de un poder ancestral que emana de los vientos del valle.\n\n"
        "<b>⚔️ Habilidades:</b>\n"
        "• Tajo de Silencio - Espada principal imbuida con voluntad ancestral\n"
        "• Diente de Penumbra - Daga capaz de cortar recuerdos\n"
        "• Equilibrio entre furia y paz - Símbolo de las dos espadas cruzadas\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 5 TON\n"
        "• Ganancia diaria: 0.15 TON\n"
        "• Duración: 60 días\n"
        "• ROI total: 9 TON (180%)\n\n"
        "Bajo su reinado, el Valle Sombrío se ha convertido en una tierra donde las criaturas olvidadas encuentran refugio.</i>"
    )
    
    # Crear botón de compra
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 5 TON", callback_data="comprar_kael_umbros")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def heroe_malrith_handler(callback: types.CallbackQuery):
    """Handler para el héroe Malrith el Eclipsado"""
    mensaje = (
        "<i><b>🕯️ Malrith el Eclipsado</b>\n\n"
        "Desde las profundidades más antiguas de la Cripta Silente, donde el eco de los cánticos prohibidos aún resuena entre los pilares corroídos, surgió Malrith, un ser devorado por las sombras pero jamás vencido. Su armadura, esculpida con los huesos de traidores y profetas caídos, resplandece con una oscuridad que parece absorber la luz misma.\n\n"
        "<b>⚔️ Habilidades:</b>\n"
        "• Sombrafinal - Espada templada en el río del olvido\n"
        "• Oráculo Nocturno - Gema que contiene el saber prohibido\n"
        "• Manifestación del miedo ancestral - Poder sobre las sombras\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1 TON\n"
        "• Ganancia diaria: 0.08 TON\n"
        "• Duración: 30 días\n"
        "• ROI total: 2.4 TON (140%)\n\n"
        "Malrith no busca conquistas típicas —él desea silenciar la memoria del mundo y cubrir cada amanecer con el manto eterno del crepúsculo.</i>"
    )
    
    # Crear botón de compra
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1 TON", callback_data="comprar_malrith")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_hada_handler(callback: types.CallbackQuery):
    """Handler para la criatura Hada"""
    mensaje = (
        "<i><b>🧚‍♀️ Hada</b>\n\n"
        "Seres mágicos de los bosques encantados que traen buena fortuna y protección a sus dueños.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.10 TON\n"
        "• Producción diaria: 1.00%\n"
        "• Ganancia diaria: 0.0010 TON\n"
        "• ROI: 70%\n"
        "• ROI total: 0.17 TON\n"
        "• Tiempo de vida: 100 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.10 TON", callback_data="comprar_hada")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_elfo_handler(callback: types.CallbackQuery):
    """Handler para la criatura Elfo"""
    mensaje = (
        "<i><b>🧙‍♂️ Elfo</b>\n\n"
        "Guardianes ancestrales de la sabiduría mágica, conocedores de los secretos más profundos de la naturaleza.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.11 TON\n"
        "• Producción diaria: 1.30%\n"
        "• Ganancia diaria: 0.00143 TON\n"
        "• ROI: 75%\n"
        "• ROI total: 0.1925 TON\n"
        "• Tiempo de vida: ~77 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.11 TON", callback_data="comprar_elfo")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_dragon_handler(callback: types.CallbackQuery):
    """Handler para la criatura Dragón"""
    mensaje = (
        "<i><b>🐉 Dragón</b>\n\n"
        "Majestuosas criaturas de fuego y poder, guardianes de tesoros legendarios y maestros del cielo.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.20 TON\n"
        "• Producción diaria: 1.45%\n"
        "• Ganancia diaria: 0.0029 TON\n"
        "• ROI: 80%\n"
        "• ROI total: 0.36 TON\n"
        "• Tiempo de vida: ~69 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.20 TON", callback_data="comprar_dragon")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_orco_handler(callback: types.CallbackQuery):
    """Handler para la criatura Orco"""
    mensaje = (
        "<i><b>👹 Orco</b>\n\n"
        "Guerreros feroces de las montañas oscuras, conocidos por su fuerza bruta y resistencia en batalla.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.22 TON\n"
        "• Producción diaria: 1.50%\n"
        "• Ganancia diaria: 0.0033 TON\n"
        "• ROI: 90%\n"
        "• ROI total: 0.418 TON\n"
        "• Tiempo de vida: ~67 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.22 TON", callback_data="comprar_orco")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_gremnli_handler(callback: types.CallbackQuery):
    """Handler para la criatura Gremnli"""
    mensaje = (
        "<i><b>👺 Gremnli</b>\n\n"
        "Tramposos astutos de las cavernas subterráneas, maestros del engaño y la supervivencia.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.25 TON\n"
        "• Producción diaria: 1.55%\n"
        "• Ganancia diaria: 0.003875 TON\n"
        "• ROI: 99%\n"
        "• ROI total: 0.4975 TON\n"
        "• Tiempo de vida: ~65 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.25 TON", callback_data="comprar_gremnli")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_unicornio_handler(callback: types.CallbackQuery):
    """Handler para la criatura Unicornio"""
    mensaje = (
        "<i><b>🦄 Unicornio</b>\n\n"
        "Criaturas puras y mágicas, símbolos de pureza y poder curativo, guardianes de la luz.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.30 TON\n"
        "• Producción diaria: 1.60%\n"
        "• Ganancia diaria: 0.0048 TON\n"
        "• ROI: 110%\n"
        "• ROI total: 0.63 TON\n"
        "• Tiempo de vida: ~63 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.30 TON", callback_data="comprar_unicornio")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_genio_handler(callback: types.CallbackQuery):
    """Handler para la criatura Genio"""
    mensaje = (
        "<i><b>🧞 Genio</b>\n\n"
        "Seres de poder ilimitado, capaces de conceder deseos y manipular la realidad misma.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 0.40 TON\n"
        "• Producción diaria: 2.00%\n"
        "• Ganancia diaria: 0.0080 TON\n"
        "• ROI: 150%\n"
        "• ROI total: 1.00 TON\n"
        "• Tiempo de vida: 50 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 0.40 TON", callback_data="comprar_genio")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_kraken_handler(callback: types.CallbackQuery):
    """Handler para la criatura Kraken"""
    mensaje = (
        "<i><b>👾 Kraken</b>\n\n"
        "Titanes del océano profundo, criaturas colosales que gobiernan las aguas más oscuras.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1.20 TON\n"
        "• Producción diaria: 3.50%\n"
        "• Ganancia diaria: 0.0420 TON\n"
        "• ROI: 210%\n"
        "• ROI total: 3.72 TON\n"
        "• Tiempo de vida: ~29 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1.20 TON", callback_data="comprar_kraken")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def criatura_licantropo_handler(callback: types.CallbackQuery):
    """Handler para la criatura Licántropo"""
    mensaje = (
        "<i><b>🐺 Licántropo</b>\n\n"
        "Guerreros que se transforman bajo la luna llena, combinando la ferocidad del lobo con la inteligencia humana.\n\n"
        "<b>💰 Información de Inversión:</b>\n"
        "• Precio: 1.00 TON\n"
        "• Producción diaria: 3.00%\n"
        "• Ganancia diaria: 0.0300 TON\n"
        "• ROI: 200%\n"
        "• ROI total: 3.00 TON\n"
        "• Tiempo de vida: ~34 días</i>"
    )
    
    compra_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Comprar por 1.00 TON", callback_data="comprar_licantropo")]
    ])
    
    await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=compra_keyboard)
    await callback.answer()

async def tienda_volver_handler(callback: types.CallbackQuery):
    """Handler para volver a la tienda principal"""
    mensaje = (
        "<i><b>🛍 Tienda</b>\n\n"
        "Bienvenido a la tienda de <b>Mundo Mítico.</b>\n\n"
        "<blockquote expandable>Aquí puedes adquirir héroes y criaturas\n— Ambos esenciales para explorar el mundo y generar ganancias en TON.</blockquote>\n\n"
        "<b>Selecciona una categoría — verás los productos disponibles y obtendrás información detallada sobre cada uno.</b></i>"
    )
    
    # Crear botones de categorías
    tienda_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Héroes", callback_data="tienda_heroes"),
        InlineKeyboardButton(text="Criaturas", callback_data="tienda_criaturas")]
    ])
    
    await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=tienda_keyboard)
    await callback.answer()

