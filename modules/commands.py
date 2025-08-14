# =========================
# Importaciones
# =========================
import logging
import datetime
import os

from aiogram import Dispatcher
from aiogram.filters import Command

# Constantes

# Handlers principales
from modules.start import start_handler, verificar_suscripcion_handler, perfil_handler
from modules.referidos import referidos_handler
from modules.tareas import tareas_handler, register_tareas_handlers

# Configuración de administradores
from config.config import is_admin

from utils.logging_config import get_logger

logger = get_logger(__name__)

# =========================
# Handler de inventario
# =========================
async def inventario_handler(event):
    """Handler de inventario (funciona con mensajes y callbacks)"""
    # Determinar si es un mensaje o callback
    if hasattr(event, 'from_user'):
        user_id = event.from_user.id
        is_callback = hasattr(event, 'data')
    else:
        return
    
    from modules.inventario import mostrar_inventario_usuario
    await mostrar_inventario_usuario(event, user_id)

async def ganancias_handler(event):
    """Handler para calcular ganancias manualmente"""
    if not hasattr(event, 'from_user'):
        return
    
    user_id = event.from_user.id
    
    try:
        resultado = await calcular_ganancias_usuario(user_id)
        
        if resultado.get("ok"):
            ganancia_total = resultado["ganancia_total"]
            nfts = resultado["nfts"]
            
            mensaje = (
                "💰 <b>Ganancias Calculadas</b>\n\n"
                f"Has recibido <code>{ganancia_total:.3f} TON</code> por tus NFTs:\n\n"
            )
            
            for nft in nfts:
                mensaje += f"• {nft['cantidad']}x {nft['item']}: +{nft['ganancia_total']:.3f} TON\n"
            
            mensaje += f"\n💸 <b>Total: {ganancia_total:.3f} TON</b>\n\n"
            mensaje += "¡Tus ganancias han sido acreditadas a tu balance!"
            
        else:
            mensaje = (
                "💰 <b>Ganancias</b>\n\n"
                f"{resultado.get('msg', 'No se pudieron calcular las ganancias')}\n\n"
                "💡 Los NFTs generan ganancias automáticamente cada 24 horas."
            )
        
        await event.answer(mensaje, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error en ganancias_handler para user_id={user_id}: {e}")
        await event.answer("❌ Error al calcular ganancias. Intenta de nuevo más tarde.")



# =========================
# Registro de comandos y callbacks
# =========================
def register_commands(dp: Dispatcher):
    """Registra todos los comandos y handlers del bot"""
    logger.info("🔧 Registrando comandos y handlers...")
    
    # Handlers principales (funcionan con mensajes y callbacks)
    dp.message.register(start_handler, lambda m: m.text == "/start")
    dp.callback_query.register(start_handler, lambda c: c.data == "start_volver")
    # VERIFICACIÓN DE CANALES COMENTADA - NO ES OBLIGATORIA
    dp.callback_query.register(verificar_suscripcion_handler, lambda c: c.data == "verificar_suscripcion")
    
    dp.message.register(tareas_handler, lambda m: m.text == "/tareas")
    dp.callback_query.register(tareas_handler, lambda c: c.data == "tareas")
    
    dp.message.register(referidos_handler, lambda m: m.text == "/referidos")
    dp.callback_query.register(referidos_handler, lambda c: c.data == "referidos")
    
    # Handler de perfil
    dp.message.register(perfil_handler, lambda m: m.text == "/perfil")
    dp.callback_query.register(perfil_handler, lambda c: c.data == "perfil")
    
    # Comando para calcular ganancias manualmente
    dp.message.register(ganancias_handler, lambda m: m.text == "/ganancias")
    
    # Registrar handlers específicos de cada módulo
    register_tareas_handlers(dp)

    
    logger.info("✅ Todos los comandos y handlers registrados correctamente")