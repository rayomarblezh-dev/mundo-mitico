from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import procesar_compra_item

# Diccionario de criaturas y precios
CRIATURAS = {
    "hada": {
        "emoji": "🧚‍♀️",
        "nombre": "Hada",
        "precio": 0.10,
        "desc": "Seres mágicos de los bosques encantados que traen buena fortuna y protección a sus dueños."
    },
    "mago": {
        "emoji": "🧙‍♂️",
        "nombre": "Mago",
        "precio": 0.11,
        "desc": "Guardianes ancestrales de la sabiduría mágica, conocedores de los secretos más profundos de la naturaleza."
    },
    "dragon": {
        "emoji": "🐉",
        "nombre": "Dragón",
        "precio": 0.20,
        "desc": "Majestuosas criaturas de fuego y poder, guardianes de tesoros legendarios y maestros del cielo."
    },
    "orco": {
        "emoji": "👹",
        "nombre": "Orco",
        "precio": 0.22,
        "desc": "Guerreros feroces de las montañas oscuras, conocidos por su fuerza bruta y resistencia en batalla."
    },
    "gremnli": {
        "emoji": "👺",
        "nombre": "Gremnli",
        "precio": 0.25,
        "desc": "Tramposos astutos de las cavernas subterráneas, maestros del engaño y la supervivencia."
    },
    "unicornio": {
        "emoji": "🦄",
        "nombre": "Unicornio",
        "precio": 0.30,
        "desc": "Criaturas puras y mágicas, símbolos de pureza y poder curativo, guardianes de la luz."
    },
    "genio": {
        "emoji": "🧞",
        "nombre": "Genio",
        "precio": 0.40,
        "desc": "Seres de poder ilimitado, capaces de conceder deseos y manipular la realidad misma."
    },
    "kraken": {
        "emoji": "👾",
        "nombre": "Kraken",
        "precio": 1.20,
        "desc": "Titanes del océano profundo, criaturas colosales que gobiernan las aguas más oscuras."
    },
    "licantropo": {
        "emoji": "🐺",
        "nombre": "Licántropo",
        "precio": 1.00,
        "desc": "Guerreros que se transforman bajo la luna llena, combinando la ferocidad del lobo con la inteligencia humana."
    }
}

async def mostrar_criatura_carrito(callback: types.CallbackQuery, criatura_key: str, cantidad: int = 1):
    c = CRIATURAS[criatura_key]
    precio_total = c["precio"] * cantidad
    mensaje = (
        f"<b>{c['emoji']} {c['nombre']}</b>\n\n"
        f"{c['desc']}\n\n"
        f"<b>💰 Precio unitario:</b> <code>{c['precio']:.2f}</code> TON\n"
        f"<b>🛒 Cantidad:</b> <code>{cantidad}</code>\n"
        f"<b>💸 Total:</b> <code>{precio_total:.2f}</code> TON\n\n"
        "Ajusta la cantidad y confirma tu compra."
    )
    carrito_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"carrito_{criatura_key}_menos_{cantidad}"),
            InlineKeyboardButton(text=f"{cantidad}", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"carrito_{criatura_key}_mas_{cantidad}")
        ],
        [InlineKeyboardButton(text=f"Comprar {cantidad} por {precio_total:.2f} TON", callback_data=f"carrito_{criatura_key}_comprar_{cantidad}")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_criaturas")]
    ])
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=carrito_keyboard)
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=carrito_keyboard)
    await callback.answer()

# Generación dinámica de handlers para cada criatura
def crear_handler_criatura(key):
    async def handler(callback: types.CallbackQuery):
        await mostrar_criatura_carrito(callback, key, 1)
    handler.__name__ = f"criatura_{key}_handler"
    return handler

for key in CRIATURAS.keys():
    handler = crear_handler_criatura(key)
    globals()[handler.__name__] = handler

def get_carrito_callback_data(data):
    # Ejemplo: carrito_hada_mas_2, carrito_hada_menos_3, carrito_hada_comprar_5
    parts = data.split('_')
    if len(parts) < 4:
        return None, None, None
    criatura = parts[1]
    accion = parts[2]
    try:
        cantidad = int(parts[3])
    except Exception:
        cantidad = 1
    return criatura, accion, cantidad

async def carrito_cantidad_handler(callback: types.CallbackQuery):
    data = callback.data
    criatura, accion, cantidad = get_carrito_callback_data(data)
    if not criatura or not accion:
        await callback.answer("Acción inválida", show_alert=True)
        return
    if accion == "mas":
        cantidad += 1
    elif accion == "menos":
        cantidad = max(1, cantidad - 1)
    await mostrar_criatura_carrito(callback, criatura, cantidad)

def get_item_criatura(criatura_key):
    c = CRIATURAS[criatura_key]
    return {"tipo": "criatura", "nombre": criatura_key, "precio": c["precio"]}

async def carrito_comprar_handler(callback: types.CallbackQuery):
    data = callback.data
    criatura, accion, cantidad = get_carrito_callback_data(data)
    if accion != "comprar":
        await callback.answer("Acción inválida", show_alert=True)
        return
    user_id = callback.from_user.id
    item = get_item_criatura(criatura)
    ok = True
    resultado = {"ok": True, "msg": ""}
    for _ in range(cantidad):
        resultado = await procesar_compra_item(user_id, item)
        if not resultado["ok"]:
            ok = False
            break
    if ok:
        nombre_criatura = CRIATURAS[criatura]['nombre']
        plural = "s" if cantidad > 1 else ""
        mensaje = (
            f"<b>✅ ¡Has comprado {cantidad} {nombre_criatura}{plural}!</b>\n\n"
            f"<i>Ya {'están' if cantidad > 1 else 'está'} en tu inventario y comenzarán a producir ganancias.</i>"
        )
    else:
        mensaje = f"<b>❌ Error en compra</b>\n\n<i>{resultado['msg']}</i>"
    try:
        await callback.message.edit_text(mensaje, parse_mode="HTML")
    except Exception:
        await callback.message.answer(mensaje, parse_mode="HTML")
    await callback.answer()
