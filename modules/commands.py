# =========================
# Importaciones
# =========================
import logging
import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command

# Utils y base de datos
from utils.database import (
    es_elegible_paquete_bienvenida,
    PAQUETE_PRECIO,
    registrar_compra_paquete_bienvenida,
    usuario_compro_paquete_bienvenida,
    get_last_promo_time,
    set_last_promo_time
)

# Handlers principales
from modules.start import start_handler
from modules.referidos import referidos_handler
from modules.tareas import tareas_handler, register_tareas_handlers
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

logger = logging.getLogger(__name__)

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
    
    try:
        await mostrar_inventario_usuario(event, user_id)
        logger.info(f"Inventario mostrado correctamente para user_id={user_id}")
    except Exception as e:
        logger.error(f"Error mostrando inventario para user_id={user_id}: {e}")
        mensaje_error = "⚠️ Ocurrió un error mostrando tu inventario. Intenta de nuevo más tarde."
        if is_callback:
            await event.answer(mensaje_error, show_alert=True)
        else:
            await event.answer(mensaje_error)

# =========================
# Registro de comandos y callbacks
# =========================
def register_commands(dp: Dispatcher):
    """
    Registra todos los comandos y callbacks del bot de forma organizada.
    """

    # --- Comandos principales ---
    dp.message.register(start_handler, Command("start"))
    dp.message.register(inventario_handler, Command("inventario"))

    # --- Callbacks de menú principales (inline) ---
    dp.callback_query.register(explorar_handler, lambda c: c.data == "explorar")
    dp.callback_query.register(tienda_handler, lambda c: c.data == "tienda")
    dp.callback_query.register(inventario_handler, lambda c: c.data == "inventario")
    dp.callback_query.register(wallet_handler, lambda c: c.data == "wallet")
    dp.callback_query.register(referidos_handler, lambda c: c.data == "referidos")
    dp.callback_query.register(tareas_handler, lambda c: c.data == "tareas")
    dp.callback_query.register(start_handler, lambda c: c.data == "start_volver")
    
    # --- Handlers de mensajes ---
    dp.message.register(procesar_hash_deposito, WalletStates.esperando_hash_deposito)

    # --- Registro de handlers de módulos ---
    register_tienda_handlers(dp)
    register_criaturas_handlers(dp)
    register_nfts_handlers(dp)
    register_wallet_handlers(dp)
    register_tareas_handlers(dp)
    register_explorar_handlers(dp)
    register_inventario_handlers(dp)