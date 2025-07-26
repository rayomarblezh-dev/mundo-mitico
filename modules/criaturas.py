import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import procesar_compra_item, obtener_balance_usuario
from modules.constants import CRIATURAS_CONFIG

logger = logging.getLogger(__name__)

# Configuración de criaturas (usando configuración centralizada)
CRIATURAS = CRIATURAS_CONFIG

async def mostrar_criatura_carrito(callback: types.CallbackQuery, criatura_key: str, cantidad: int = 1):
    """Muestra el carrito de compra para una criatura específica"""
    user_id = callback.from_user.id
    
    try:
        criatura = CRIATURAS.get(criatura_key)
        if not criatura:
            await callback.answer("❌ Criatura no encontrada", show_alert=True)
            return
        
        balance = await obtener_balance_usuario(user_id)
        precio_total = criatura["precio"] * cantidad
        
        mensaje = (
            f"{criatura['emoji']} {criatura['nombre']}\n\n"
            f"{criatura['desc']}\n\n"
            f"Información:\n"
            f"• Categoría: {criatura['categoria']}\n"
            f"• Uso: {criatura['uso']}\n"
            f"• Precio unitario: {criatura['precio']:.2f} TON\n"
            f"• Cantidad: {cantidad}\n"
            f"• Total: {precio_total:.2f} TON\n\n"
            f"Tu balance: {balance:.3f} TON\n\n"
            "Ajusta la cantidad y confirma tu compra."
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="➖", callback_data=f"carrito_{criatura_key}_menos_{cantidad}")
        builder.button(text=f"{cantidad}", callback_data="noop")
        builder.button(text="➕", callback_data=f"carrito_{criatura_key}_mas_{cantidad}")
        builder.button(text=f"💎 Comprar {cantidad} por {precio_total:.2f} TON", callback_data=f"carrito_{criatura_key}_comprar_{cantidad}")
        builder.button(text="🔙 Volver", callback_data="tienda_criaturas")
        builder.adjust(3, 1, 1)
        keyboard = builder.as_markup()
        
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en mostrar_criatura_carrito para user_id={user_id}, criatura={criatura_key}: {e}")
        await callback.answer("❌ Error al mostrar criatura", show_alert=True)
    
    await callback.answer()

def crear_handler_criatura(key):
    """Crea un handler dinámico para una criatura específica"""
    async def handler(callback: types.CallbackQuery):
        await mostrar_criatura_carrito(callback, key, 1)
    handler.__name__ = f"criatura_{key}_handler"
    return handler

# Generar handlers dinámicamente para cada criatura
for key in CRIATURAS.keys():
    handler = crear_handler_criatura(key)
    globals()[handler.__name__] = handler

def get_carrito_callback_data(data):
    """Extrae información del callback data del carrito"""
    # Ejemplo: carrito_hada_mas_2, carrito_hada_menos_3, carrito_hada_comprar_5
    parts = data.split("_")
    if len(parts) >= 4:
        criatura_key = parts[1]
        accion = parts[2]
        cantidad = int(parts[3])
        return criatura_key, accion, cantidad
    return None, None, None

async def carrito_cantidad_handler(callback: types.CallbackQuery):
    """Handler para ajustar cantidad en el carrito"""
    user_id = callback.from_user.id
    
    try:
        criatura_key, accion, cantidad_actual = get_carrito_callback_data(callback.data)
        
        if not criatura_key or not accion:
            await callback.answer("❌ Datos inválidos", show_alert=True)
            return
        
        if accion == "mas":
            nueva_cantidad = cantidad_actual + 1
        elif accion == "menos":
            nueva_cantidad = max(1, cantidad_actual - 1)
        else:
            await callback.answer("❌ Acción no válida", show_alert=True)
            return
        
        await mostrar_criatura_carrito(callback, criatura_key, nueva_cantidad)
        
    except Exception as e:
        logger.error(f"Error en carrito_cantidad_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al ajustar cantidad", show_alert=True)

def get_item_criatura(criatura_key):
    """Obtiene la configuración de item para una criatura"""
    criatura = CRIATURAS.get(criatura_key)
    if not criatura:
        return None
    
    return {
        "tipo": "criatura",
        "nombre": criatura_key,
        "precio": criatura["precio"]
    }

async def carrito_comprar_handler(callback: types.CallbackQuery):
    """Handler para procesar la compra de criaturas"""
    user_id = callback.from_user.id
    
    try:
        criatura_key, accion, cantidad = get_carrito_callback_data(callback.data)
        
        if not criatura_key or accion != "comprar":
            await callback.answer("❌ Datos inválidos", show_alert=True)
            return
        
        criatura = CRIATURAS.get(criatura_key)
        if not criatura:
            await callback.answer("❌ Criatura no encontrada", show_alert=True)
            return
        
        # Procesar compra
        item = get_item_criatura(criatura_key)
        if not item:
            await callback.answer("❌ Error en configuración de criatura", show_alert=True)
            return
        
        # Ajustar precio por cantidad
        item["precio"] = item["precio"] * cantidad
        
        resultado = await procesar_compra_item(user_id, item)
        
        if resultado.get("ok"):
            mensaje = (
                f"✅ ¡Compra Exitosa!\n\n"
                f"🎉 ¡Has adquirido {cantidad} {criatura['emoji']} {criatura['nombre']}!\n\n"
                f"💰 Información de la compra:\n"
                f"• Cantidad: {cantidad}\n"
                f"• Precio unitario: {criatura['precio']:.2f} TON\n"
                f"• Total pagado: {item['precio']:.2f} TON\n"
                f"• Categoría: {criatura['categoria']}\n"
                f"• Uso: {criatura['uso']}\n\n"
                f"Todas las criaturas han sido añadidas a tu inventario.\n"
                f"¡Ahora puedes usarlas en las actividades de Explorar!"
            )
        else:
            mensaje = (
                f"❌ Error en la Compra\n\n"
                f"{resultado.get('msg', 'Ha ocurrido un error inesperado.')}\n\n"
                f"💡 Posibles causas:\n"
                f"• Balance insuficiente\n"
                f"• Error en el sistema\n"
                f"• Cantidad inválida"
            )
        
        # Botones para volver
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_criaturas")],
            [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
        ])
        
        try:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        except Exception:
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
            
    except Exception as e:
        logger.error(f"Error en carrito_comprar_handler para user_id={user_id}: {e}")
        await callback.answer("❌ Error al procesar la compra", show_alert=True)
    
    await callback.answer()

def register_criaturas_handlers(dp):
    """Registra todos los handlers del módulo criaturas"""
    # Callbacks de carrito
    dp.callback_query.register(carrito_cantidad_handler, lambda c: c.data.startswith("carrito_") and ("_mas_" in c.data or "_menos_" in c.data))
    dp.callback_query.register(carrito_comprar_handler, lambda c: c.data.startswith("carrito_") and "_comprar_" in c.data)
    
    # Handlers dinámicos para cada criatura
    for criatura_key in CRIATURAS.keys():
        handler_name = f"criatura_{criatura_key}_handler"
        if handler_name in globals():
            dp.callback_query.register(globals()[handler_name], lambda c, key=criatura_key: c.data == f"criatura_{key}")
