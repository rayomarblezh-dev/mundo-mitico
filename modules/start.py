from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import procesar_nuevo_referido, obtener_usuario_por_username
import datetime
import logging

logger = logging.getLogger(__name__)

# Importar configuración de canales
from config.config import REQUIRED_CHANNELS

# Configuración de canales requeridos
CANALES_REQUERIDOS = REQUIRED_CHANNELS

# VERIFICACIÓN DE CANALES COMENTADA - NO ES OBLIGATORIA
# async def verificar_suscripcion_canales(bot, user_id: int) -> tuple[bool, list]:
#     """
#     Verifica si el usuario está suscrito a los canales requeridos.
#     
#     Args:
#         bot: Instancia del bot
#         user_id: ID del usuario
#         
#     Returns:
#         Tuple con (está_suscrito, canales_faltantes)
#     """
#     canales_faltantes = []
#     
#     for canal in CANALES_REQUERIDOS:
#         try:
#             # Intentar obtener el estado del usuario en el canal
#             chat_member = await bot.get_chat_member(canal["id"], user_id)
#             
#             # Verificar si el usuario está suscrito
#             if chat_member.status in ["left", "kicked"]:
#                 canales_faltantes.append(canal)
#                 
#         except Exception as e:
#             logger.warning(f"Error verificando suscripción a {canal['id']} para user_id={user_id}: {e}")
#             canales_faltantes.append(canal)
#     
#     return len(canales_faltantes) == 0, canales_faltantes

# def crear_teclado_verificacion_canales(canales_faltantes: list) -> InlineKeyboardMarkup:
#     """
#     Crea el teclado para la verificación de canales con estilo similar a la imagen.
#     
#     Args:
#         canales_faltantes: Lista de canales a los que el usuario debe suscribirse
#         
#     Returns:
#         Teclado inline con botones de verificación
#     """
#     builder = InlineKeyboardBuilder()
#     
#     for canal in canales_faltantes:
#         builder.button(text=f"Unirse a {canal['nombre']}", url=canal['url'])
#     
#     builder.button(text="✅ Verificar union", callback_data="verificar_suscripcion")
#     builder.adjust(1)
#     
#     return builder.as_markup()

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
    
    # Verificar si el usuario ya existe
    usuario = await usuarios_col.find_one({"user_id": user_id})
    
    if not usuario:
        # Usuario nuevo - crear usuario
        await usuarios_col.insert_one({
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "balance": 0.0,
            "fecha_registro": datetime.datetime.now(),
            "activo": True
        })
        usuario = await usuarios_col.find_one({"user_id": user_id})
    
    # VERIFICACIÓN DE CANALES COMENTADA - NO ES OBLIGATORIA
    # # Usuario existe - verificar canales
    # if not is_callback:  # Solo verificar en mensajes directos, no en callbacks
    #     esta_suscrito, canales_faltantes = await verificar_suscripcion_canales(event.bot, user_id)
    #     
    #     if not esta_suscrito:
    #         mensaje_verificacion = (
    #             "<b>Debes unirte a todos nuestros canales.\n\n"
    #             "Una vez te hayas unido, haz clic en 'Verificar union' para continuar.</b>\n\n"
    #         )
    #         keyboard = crear_teclado_verificacion_canales(canales_faltantes)
    #         
    #         await event.answer(mensaje_verificacion, parse_mode="HTML", reply_markup=keyboard)
    #         return
    
    # Usuario existe - ir directamente al menú (sin verificación de canales)

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
        "🌍 <b>¡Bienvenido a Mundo Mítico!\n\n"
        "Sumérgete en un universo épico donde las criaturas legendarias aguardan ser descubiertas. En este mundo de aventuras, podrás:\n"
        "<blockquote expandable>— Cazar Criaturas - Encuentra y captura bestias míticas\n"
        "— Expediciones - Explora territorios desconocidos\n"
        "— Combates Épicos - Enfréntate a desafíos legendarios\n"
        "— Invertir TON - Gestiona tu economía en el mundo mítico\n"
        "— Generar Ganancias - Atrapa criaturas y compra héroes que producen diariamente</blockquote>\n"
        "¡Tu aventura comienza ahora! Elige tu camino y forja tu leyenda en este mundo.\n\n"
        "Accesos rápidos:</b>"
    )

    # Crear teclado inline con todos los botones (incluyendo Tareas)
    builder = InlineKeyboardBuilder()
    builder.button(text="🌍 Explorar", callback_data="explorar")
    builder.button(text="🛍 Tienda", callback_data="tienda")
    builder.button(text="🧳 Inventario", callback_data="inventario")
    builder.button(text="👛 Wallet", callback_data="wallet")
    builder.button(text="👥 Referidos", callback_data="referidos")
    builder.button(text="📋 Tareas", callback_data="tareas")
    builder.button(text="📮 Soporte", url="http://t.me/wolfpromot")
    builder.adjust(1, 2, 1, 2, 1)
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
    
# VERIFICACIÓN DE CANALES COMENTADA - NO ES OBLIGATORIA
# async def verificar_suscripcion_handler(callback: types.CallbackQuery):
#     """Handler para verificar la suscripción a canales"""
#     user_id = callback.from_user.id
#     
#     try:
#         # Verificar suscripción nuevamente
#         esta_suscrito, canales_faltantes = await verificar_suscripcion_canales(callback.bot, user_id)
#         
#         if esta_suscrito:
#             # Usuario está suscrito, ir directamente al menú
#             await callback.answer("✅ ¡Bienvenido a Mundo Mítico!", show_alert=True)
#             
#             # Llamar al start_handler para mostrar el menú principal
#             await start_handler(callback)
#             
#         else:
#             # Usuario aún no está suscrito
#             await callback.answer("❌ Aún no estás suscrito a todos los canales requeridos.", show_alert=True)
#             
#     except Exception as e:
#         logger.error(f"Error en verificar_suscripcion_handler para user_id={user_id}: {e}")
#         await callback.answer("❌ Error al verificar suscripción. Intenta de nuevo.", show_alert=True)
#     
#     await callback.answer()