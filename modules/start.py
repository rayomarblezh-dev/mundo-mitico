from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import procesar_nuevo_referido, obtener_usuario_por_username
import datetime

async def start_handler(event):
    """Handler de start (funciona con mensajes y callbacks)"""
    # Determinar si es un mensaje o callback
    if hasattr(event, 'from_user'):
        user_id = event.from_user.id
        username = event.from_user.username
        first_name = event.from_user.first_name
        is_callback = hasattr(event, 'data')
    else:
        return
    
    # Importación local para evitar import circular
    from utils.database import usuarios_col
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

    # Manejo de referidos mejorado
    args = None
    if hasattr(event, 'text') and event.text:
        parts = event.text.split(maxsplit=1)
        if len(parts) > 1:
            args = parts[1]
    if args:
        if args.startswith("ref_"):
            try:
                referidor_id = int(args.replace("ref_", ""))
                if referidor_id != user_id:
                    # Obtener nombres para las notificaciones
                    referidor = await obtener_usuario_por_username(username) or await usuarios_col.find_one({"user_id": referidor_id})
                    referidor_name = referidor.get("first_name", "Usuario") if referidor else "Usuario"
                    referido_name = first_name or username or "Usuario"
                    
                    # Procesar referido con notificaciones
                    await procesar_nuevo_referido(
                        event.bot, 
                        referidor_id, 
                        user_id, 
                        referido_name, 
                        referidor_name
                    )
            except ValueError:
                pass  # El argumento no es un número válido
            except Exception as e:
                print(f"Error al procesar referido: {e}")

    welcome_text = (
        "🌍 ¡Bienvenido a Mundo Mítico!\n\n"
        "Sumérgete en un universo épico donde las criaturas legendarias aguardan ser descubiertas. En este mundo de aventuras, podrás:\n"
        "— Cazar Criaturas - Encuentra y captura bestias míticas\n"
        "— Expediciones - Explora territorios desconocidos\n"
        "— Combates Épicos - Enfréntate a desafíos legendarios\n"
        "— Invertir TON - Gestiona tu economía en el mundo mítico\n"
        "— Generar Ganancias - Atrapa criaturas y compra héroes que producen diariamente\n\n"
        "¡Tu aventura comienza ahora! Elige tu camino y forja tu leyenda en este mundo.\n\n"
        "Accesos rápidos:"
    )

    # Crear teclado inline con todos los botones (incluyendo Tareas)
    builder = InlineKeyboardBuilder()
    builder.button(text="🌍 Explorar", callback_data="explorar")
    builder.button(text="🛍 Tienda", callback_data="tienda")
    builder.button(text="🧳 Inventario", callback_data="inventario")
    builder.button(text="👛 Wallet", callback_data="wallet")
    builder.button(text="👥 Referidos", callback_data="referidos")
    builder.button(text="📋 Tareas", callback_data="tareas")
    builder.button(text="📣 Canal", url="https://t.me/MundoMitico")
    builder.button(text="📮 Soporte", url="http://t.me/wolfpromot")
    builder.adjust(2, 2, 2, 2)
    keyboard = builder.as_markup()

    # Enviar mensaje según el tipo de evento
    if is_callback:
        try:
            await event.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            if "message is not modified" in str(e):
                # El mensaje es el mismo, solo responder al callback
                pass
            else:
                # Otro error, intentar enviar nuevo mensaje
                await event.message.answer(welcome_text, parse_mode="HTML", reply_markup=keyboard)
        await event.answer()
    else:
        await event.answer(welcome_text, parse_mode="HTML", reply_markup=keyboard)
    
    
