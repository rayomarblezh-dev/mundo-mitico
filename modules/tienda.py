import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import es_elegible_paquete_bienvenida, procesar_compra_item, obtener_balance_usuario
from modules.constants import CRIATURAS_CONFIG, PAQUETE_PRECIO

logger = logging.getLogger(__name__)

async def tienda_handler(event):
    """Handler principal de la tienda (funciona con mensajes y callbacks)"""
    # Determinar si es un mensaje o callback
    if hasattr(event, 'from_user'):
        user_id = event.from_user.id
        is_callback = hasattr(event, 'data')
    else:
        return
    
    try:
        balance = await obtener_balance_usuario(user_id)
        
        mensaje = (
            "🛍️ Tienda\n\n"
            "Bienvenido a la tienda más mágica del universo!\n\n"
            f"Balance: {balance:.3f} TON\n\n"
            "Categorías disponibles:\n"
            "• Criaturas - Seres mágicos para explorar y combatir\n"
            "• NFTs - Colecciones únicas que generan ganancias\n"
            "• Promociones - Ofertas especiales y paquetes\n\n"
            "Consejo: Las criaturas te ayudan en exploraciones y los NFTs generan TON diariamente."
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🐾 Criaturas", callback_data="tienda_criaturas")
        builder.button(text="🎨 NFTs", callback_data="tienda_nfts")
        builder.button(text="🔥 Promociones", callback_data="tienda_promos")
        builder.button(text="🔙 Volver", callback_data="start_volver")
        builder.adjust(2, 1, 1)
        keyboard = builder.as_markup()
        
        # Enviar mensaje según el tipo de evento
        if is_callback:
            try:
                await event.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
            except Exception as e:
                if "message is not modified" in str(e):
                    # El mensaje es el mismo, solo responder al callback
                    pass
                else:
                    # Otro error, intentar enviar nuevo mensaje
                    await event.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            await event.answer()
        else:
            await event.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en tienda_handler para user_id={user_id}: {e}")
        if is_callback:
            await event.answer("❌ Error al cargar la tienda. Intenta de nuevo más tarde.", show_alert=True)
        else:
            await event.answer("❌ Error al cargar la tienda. Intenta de nuevo más tarde.")

async def tienda_criaturas_handler(callback: types.CallbackQuery):
    """Handler para mostrar la sección de criaturas"""
    user_id = callback.from_user.id
    
    try:
        balance = await obtener_balance_usuario(user_id)
        
        mensaje = (
            "🐾 Criaturas Míticas\n\n"
            "Descubre y adquiere seres mágicos con poderes únicos.\n\n"
            f"Balance: {balance:.3f} TON\n\n"
            "Tipos de criaturas:\n"
            "• Básicas - Hadas, Magos, Orcos\n"
            "• Intermedias - Dragones, Unicornios, Genios\n"
            "• Avanzadas - Kraken, Licántropos\n\n"
            "Uso: Las criaturas son necesarias para actividades en Explorar."
        )
        
        builder = InlineKeyboardBuilder()
        # Generar botones dinámicamente desde la configuración centralizada
        for criatura_key, criatura_config in CRIATURAS_CONFIG.items():
            emoji = criatura_config["emoji"]
            nombre = criatura_config["nombre"]
            precio = criatura_config["precio"]
            builder.button(text=f"{emoji} {nombre}", callback_data=f"criatura_{criatura_key}")
        
        builder.button(text="🔙 Volver", callback_data="tienda_volver")
        builder.button(text="🏠 Menú Principal", callback_data="start_volver")
        builder.adjust(2)
        keyboard = builder.as_markup()
        
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            if "message is not modified" in str(e):
                # El mensaje es el mismo, solo responder al callback
                pass
            else:
                # Otro error, intentar enviar nuevo mensaje
                await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en tienda_criaturas_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al cargar criaturas", show_alert=True)
    
    await callback.answer()

async def tienda_volver_handler(callback: types.CallbackQuery):
    """Handler para volver al menú principal de la tienda"""
    user_id = callback.from_user.id
    
    try:
        balance = await obtener_balance_usuario(user_id)
        
        mensaje = (
            "🛍️ Tienda de Mundo Mítico\n\n"
            "¡Bienvenido a la tienda más mágica del universo!\n\n"
            f"Balance: {balance:.3f} TON\n\n"
            "Categorías disponibles:\n"
            "• Criaturas - Seres mágicos para explorar y combatir\n"
            "• NFTs - Colecciones únicas que generan ganancias\n"
            "• Promociones - Ofertas especiales y paquetes\n\n"
            "Consejo: Las criaturas te ayudan en exploraciones y los NFTs generan TON diariamente."
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🐾 Criaturas", callback_data="tienda_criaturas")
        builder.button(text="🎨 NFTs", callback_data="tienda_nfts")
        builder.button(text="🔥 Promociones", callback_data="tienda_promos")
        builder.button(text="🔙 Volver", callback_data="start_volver")
        builder.adjust(2, 1, 1)
        keyboard = builder.as_markup()
        
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            if "message is not modified" in str(e):
                # El mensaje es el mismo, solo responder al callback
                pass
            else:
                # Otro error, intentar enviar nuevo mensaje
                await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en tienda_volver_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al volver a la tienda", show_alert=True)
    
    await callback.answer()

async def tienda_promos_handler(callback: types.CallbackQuery):
    """Handler para mostrar promociones disponibles"""
    user_id = callback.from_user.id
    
    try:
        balance = await obtener_balance_usuario(user_id)
        es_elegible = await es_elegible_paquete_bienvenida(user_id)
        
        mensaje = (
            "🔥 Promociones Especiales\n\n"
            "¡Ofertas únicas por tiempo limitado!\n\n"
            f"Balance: {balance:.3f} TON\n\n"
        )
        
        builder = InlineKeyboardBuilder()
        
        if es_elegible:
            mensaje += (
                "💎 Paquete de Bienvenida\n"
                "• 7 🧚‍♀️ Hadas\n"
                "• 3 🧙‍♂️ Magos\n"
                "• 1 🐺 Licántropo\n"
                "• Precio: 1.5 TON\n"
                "• Válido: Solo por 15 días desde tu registro\n\n"
                "¡Perfecto para comenzar tu aventura!"
            )
            builder.button(text="💎 Comprar", callback_data="comprar_paquete_bienvenida")
        else:
            mensaje += (
                "📢 No hay promociones disponibles\n\n"
                "Actualmente no tienes promociones activas.\n"
                "¡Mantente atento a futuras ofertas especiales!"
            )
        
        builder.button(text="🔙 Volver", callback_data="tienda_volver")
        builder.button(text="🏠 Menú Principal", callback_data="start_volver")
        builder.adjust(1)
        keyboard = builder.as_markup()
        
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            if "message is not modified" in str(e):
                # El mensaje es el mismo, solo responder al callback
                pass
            else:
                # Otro error, intentar enviar nuevo mensaje
                await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en tienda_promos_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al cargar promociones", show_alert=True)
    
    await callback.answer()

async def comprar_paquete_bienvenida_handler(callback: types.CallbackQuery):
    """Handler para comprar el paquete de bienvenida"""
    user_id = callback.from_user.id
    
    try:
        # Verificar elegibilidad
        es_elegible = await es_elegible_paquete_bienvenida(user_id)
        if not es_elegible:
            await callback.answer("❌ No eres elegible para esta promoción", show_alert=True)
            return
        
        # Procesar compra
        item = {
            "tipo": "promo", 
            "nombre": "paquete_bienvenida", 
            "precio": PAQUETE_PRECIO
        }
        
        resultado = await procesar_compra_item(user_id, item)
        
        if resultado.get("ok"):
            mensaje = (
                "✅ ¡Compra Exitosa!\n\n"
                "¡Has adquirido el Paquete de Bienvenida!\n\n"
                "Contenido del paquete:\n"
                "• 7 🧚‍♀️ Hadas\n"
                "• 3 🧙‍♂️ Magos\n"
                "• 1 🐺 Licántropo\n\n"
                f"Precio pagado: {PAQUETE_PRECIO} TON\n"
                "Valor real: 3.0 TON (¡50% de descuento!)\n\n"
                "Todas las criaturas han sido añadidas a tu inventario.\n"
                "¡Ahora puedes explorar el mundo con tu nuevo ejército mágico!"
            )
        else:
            mensaje = (
                "❌ Error en la Compra\n\n"
                f"{resultado.get('msg', 'Ha ocurrido un error inesperado.')}\n\n"
                "Posibles causas:\n"
                "• Balance insuficiente\n"
                "• Promoción expirada\n"
                "• Ya compraste este paquete"
            )
        
        # Botones para volver
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_promos")],
            [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
        ])
        
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
            
    except Exception as e:
        logger.error(f"Error en comprar_paquete_bienvenida_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al procesar la compra", show_alert=True)
    
    await callback.answer()

def register_tienda_handlers(dp):
    """Registra todos los handlers del módulo tienda"""
    # Callbacks principales
    dp.callback_query.register(tienda_criaturas_handler, lambda c: c.data == "tienda_criaturas")
    dp.callback_query.register(tienda_volver_handler, lambda c: c.data == "tienda_volver")
    dp.callback_query.register(tienda_promos_handler, lambda c: c.data == "tienda_promos")
    dp.callback_query.register(comprar_paquete_bienvenida_handler, lambda c: c.data == "comprar_paquete_bienvenida")
    
    # Callback para NFTs (redirige al módulo NFTs)
    from modules.nfts import nfts_handler
    dp.callback_query.register(nfts_handler, lambda c: c.data == "tienda_nfts")