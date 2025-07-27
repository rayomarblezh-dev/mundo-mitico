# =========================
# Importaciones
# =========================
import logging
import datetime
import os

from aiogram import Dispatcher
from aiogram.filters import Command

# Utils y base de datos
from utils.database import (
    es_elegible_paquete_bienvenida,
    registrar_compra_paquete_bienvenida,
    usuario_compro_paquete_bienvenida,
    get_last_promo_time,
    set_last_promo_time
)

# Constantes
from modules.constants import PAQUETE_PRECIO

# Handlers principales
from modules.start import start_handler
from modules.referidos import referidos_handler
from modules.tareas import tareas_handler, register_tareas_handlers

# Configuración de administradores
from config.config import is_admin
from modules.tienda import (
    tienda_handler,
    tienda_criaturas_handler,
    tienda_volver_handler,
    register_tienda_handlers
)
from modules.criaturas import register_criaturas_handlers
from modules.wallet import (
    wallet_handler,
    register_wallet_handlers,
    procesar_hash_deposito,
    WalletStates,
)
from modules.explorar import explorar_handler, register_explorar_handlers
from modules.nfts import register_nfts_handlers
from modules.inventario import mostrar_inventario_usuario, register_inventario_handlers
from modules.ganancias_diarias import calcular_ganancias_usuario

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
    # dp.callback_query.register(verificar_suscripcion_handler, lambda c: c.data == "verificar_suscripcion")
    
    dp.message.register(wallet_handler, lambda m: m.text == "/wallet")
    dp.callback_query.register(wallet_handler, lambda c: c.data == "wallet")
    dp.callback_query.register(wallet_handler, lambda c: c.data == "wallet_volver")
    
    dp.message.register(tienda_handler, lambda m: m.text == "/tienda")
    dp.callback_query.register(tienda_handler, lambda c: c.data == "tienda")
    
    dp.message.register(inventario_handler, lambda m: m.text == "/inventario")
    dp.callback_query.register(inventario_handler, lambda c: c.data == "inventario")
    
    dp.message.register(explorar_handler, lambda m: m.text == "/explorar")
    dp.callback_query.register(explorar_handler, lambda c: c.data == "explorar")
    
    dp.message.register(tareas_handler, lambda m: m.text == "/tareas")
    dp.callback_query.register(tareas_handler, lambda c: c.data == "tareas")
    
    dp.message.register(referidos_handler, lambda m: m.text == "/referidos")
    dp.callback_query.register(referidos_handler, lambda c: c.data == "referidos")
    
    # Comando para calcular ganancias manualmente
    dp.message.register(ganancias_handler, lambda m: m.text == "/ganancias")
    
    # Registrar handlers específicos de cada módulo
    register_wallet_handlers(dp)
    register_tienda_handlers(dp)
    register_inventario_handlers(dp)
    register_explorar_handlers(dp)
    register_criaturas_handlers(dp)
    register_nfts_handlers(dp)
    register_tareas_handlers(dp)

    
    logger.info("✅ Todos los comandos y handlers registrados correctamente")