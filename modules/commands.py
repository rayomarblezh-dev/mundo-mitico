# =========================
# Importaciones
# =========================
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import es_elegible_paquete_bienvenida, PAQUETE_PRECIO, registrar_compra_paquete_bienvenida, usuario_compro_paquete_bienvenida
from utils.database import get_last_promo_time, set_last_promo_time
import datetime
import logging
logger = logging.getLogger(__name__)

from modules.start import start_handler
from modules.guia import guia_callback_handler
from modules.referidos import referidos_handler
from modules.tienda import (
    tienda_handler,
    tienda_criaturas_handler,
    tienda_volver_handler,
    register_tienda_handlers
)

from modules.criaturas import (
    mostrar_criatura_carrito,
    carrito_cantidad_handler,
    carrito_comprar_handler,
    # Handlers individuales generados dinámicamente:
    criatura_hada_handler,
    criatura_mago_handler,
    criatura_dragon_handler,
    criatura_orco_handler,
    criatura_gremnli_handler,
    criatura_unicornio_handler,
    criatura_genio_handler,
    criatura_kraken_handler,
    criatura_licantropo_handler
)
from modules.wallet import (
    wallet_handler,
    wallet_depositar_handler,
    wallet_retirar_handler,
    handle_deposit_network,
    procesar_wallet_ton,
    procesar_cantidad_retiro,
    confirmar_retiro_handler,
    cancelar_retiro_handler,
    WalletStates,
    procesar_hash_deposito,  # Importar el nuevo handler
    procesar_cantidad_deposito,
    cancelar_deposito_handler,
    cancelar_retiro_total_handler,
    register_wallet_handlers,
)
from modules.explorar import explorar_handler
from modules.nfts import (
    nfts_handler,
    nft_moguri_handler,
    nft_gargola_handler,
    nft_ghost_handler,
    comprar_nft_moguri_handler,
    comprar_nft_gargola_handler,
    comprar_nft_ghost_handler
)
from modules.admin import (
    admin_handler,
    procesar_user_id,
    procesar_cantidad_admin,
    procesar_razon_admin,
    confirmar_credito_handler,
    cancelar_credito_handler,
    admin_estadisticas_handler,
    admin_depositos_handler,
    admin_importante_handler,
    AdminStates,
    info_handler,
    admin_tareas_handler,
    aceptar_deposito_handler,
    admin_retiros_handler,
    aceptar_retiro_handler,
    admin_resumen_fondos_handler,
    admin_buscar_handler,
    BuscarStates,
    procesar_busqueda_usuario,
    paginacion_busqueda_handler,
)
from modules.inventario import mostrar_inventario_usuario


async def inventario_handler(message):
    from modules.inventario import mostrar_inventario_usuario
    try:
        await mostrar_inventario_usuario(message, message.from_user.id)
        logging.info(f"Inventario mostrado correctamente para user_id={message.from_user.id}")
    except Exception as e:
        logging.error(f"Error mostrando inventario para user_id={message.from_user.id}: {e}")
        await message.answer("⚠️ Ocurrió un error mostrando tu inventario. Intenta de nuevo más tarde.")


# =========================
# Registro de comandos
# =========================
# Eliminar función mostrar_promo_paquete_bienvenida y el handler comprar_paquete_bienvenida_handler

def register_commands(dp: Dispatcher):
    """
    Registrar todos los comandos del bot
    """

    # =========================
    # Comando /start
    # =========================
    dp.message.register(start_handler, Command("start"))
    
    # =========================
    # Comando /inventario
    # =========================
    dp.message.register(inventario_handler, Command("inventario"))
    
    # =========================
    # Comando /admin
    # =========================
    dp.message.register(admin_handler, Command("admin"))
    
    # =========================
    # Comando /info
    # =========================
    dp.message.register(info_handler, Command("info"))
    
    # =========================
    # Callbacks de tienda
    # =========================
    dp.callback_query.register(tienda_criaturas_handler, lambda c: c.data == "tienda_criaturas")
    dp.callback_query.register(tienda_volver_handler, lambda c: c.data == "tienda_volver")
    dp.callback_query.register(nfts_handler, lambda c: c.data == "tienda_nfts")
    
    # =========================
    # Callbacks de criaturas
    # =========================
    # Handlers de carrito de criaturas
    dp.callback_query.register(carrito_cantidad_handler, lambda c: c.data.startswith("carrito_") and ("_mas_" in c.data or "_menos_" in c.data))
    dp.callback_query.register(carrito_comprar_handler, lambda c: c.data.startswith("carrito_") and "_comprar_" in c.data)
    # Handlers de criaturas para mostrar el carrito
    dp.callback_query.register(criatura_hada_handler, lambda c: c.data == "criatura_hada")
    dp.callback_query.register(criatura_mago_handler, lambda c: c.data == "criatura_mago")
    dp.callback_query.register(criatura_dragon_handler, lambda c: c.data == "criatura_dragon")
    dp.callback_query.register(criatura_orco_handler, lambda c: c.data == "criatura_orco")
    dp.callback_query.register(criatura_gremnli_handler, lambda c: c.data == "criatura_gremnli")
    dp.callback_query.register(criatura_unicornio_handler, lambda c: c.data == "criatura_unicornio")
    dp.callback_query.register(criatura_genio_handler, lambda c: c.data == "criatura_genio")
    dp.callback_query.register(criatura_kraken_handler, lambda c: c.data == "criatura_kraken")
    dp.callback_query.register(criatura_licantropo_handler, lambda c: c.data == "criatura_licantropo")

    # =========================
    # Callbacks de NFTs
    # =========================
    dp.callback_query.register(nfts_handler, lambda c: c.data == "tienda_nfts")
    dp.callback_query.register(nft_moguri_handler, lambda c: c.data == "nft_moguri")
    dp.callback_query.register(nft_gargola_handler, lambda c: c.data == "nft_gargola")
    dp.callback_query.register(nft_ghost_handler, lambda c: c.data == "nft_ghost")
    dp.callback_query.register(comprar_nft_moguri_handler, lambda c: c.data == "comprar_nft_moguri")
    dp.callback_query.register(comprar_nft_gargola_handler, lambda c: c.data == "comprar_nft_gargola")
    dp.callback_query.register(comprar_nft_ghost_handler, lambda c: c.data == "comprar_nft_ghost")

    # =========================
    # Callbacks de wallet
    # =========================
    dp.callback_query.register(wallet_depositar_handler, lambda c: c.data == "wallet_depositar")
    dp.callback_query.register(wallet_retirar_handler, lambda c: c.data == "wallet_retirar")
    # Handlers para redes de depósito
    dp.callback_query.register(handle_deposit_network, lambda c: c.data.startswith("depositar_"))
    # Handler para procesar wallet TON (con FSM)
    dp.message.register(procesar_wallet_ton, WalletStates.waiting_for_wallet)
    # Handler para procesar cantidad de retiro (con FSM)
    dp.message.register(procesar_cantidad_retiro, WalletStates.waiting_for_amount)
    # Handler para procesar cantidad de depósito (con FSM)
    dp.message.register(procesar_cantidad_deposito, WalletStates.waiting_for_deposit_amount)
    # Handlers para confirmar/cancelar retiro
    dp.callback_query.register(confirmar_retiro_handler, lambda c: c.data == "confirmar_retiro")
    dp.callback_query.register(cancelar_retiro_handler, lambda c: c.data == "cancelar_retiro")
    # Handlers para cancelar depósito y retiro total
    dp.callback_query.register(cancelar_deposito_handler, lambda c: c.data == "cancelar_deposito")
    dp.callback_query.register(cancelar_retiro_total_handler, lambda c: c.data == "cancelar_retiro_total")
    # Registrar handlers agrupados
    register_wallet_handlers(dp)
    
    # =========================
    # Callbacks de administración
    # =========================
    dp.callback_query.register(admin_buscar_handler, lambda c: c.data == "admin_buscar")
    dp.message.register(procesar_busqueda_usuario, BuscarStates.waiting_for_user)
    dp.callback_query.register(admin_tareas_handler, lambda c: c.data == "admin_tareas")
    dp.callback_query.register(confirmar_credito_handler, lambda c: c.data == "admin_confirmar_credito")
    dp.callback_query.register(cancelar_credito_handler, lambda c: c.data == "admin_cancelar_credito")
    dp.callback_query.register(admin_estadisticas_handler, lambda c: c.data == "admin_estadisticas")
    dp.callback_query.register(admin_depositos_handler, lambda c: c.data == "admin_depositos")
    dp.callback_query.register(aceptar_deposito_handler, lambda c: c.data.startswith("aceptar_deposito_"))
    dp.callback_query.register(admin_importante_handler, lambda c: c.data == "admin_importante")
    dp.callback_query.register(admin_retiros_handler, lambda c: c.data == "admin_retiros")
    dp.callback_query.register(aceptar_retiro_handler, lambda c: c.data.startswith("aceptar_retiro_"))
    dp.callback_query.register(admin_resumen_fondos_handler, lambda c: c.data == "admin_resumen_fondos")
    dp.callback_query.register(paginacion_busqueda_handler, lambda c: c.data in ["dep_prev", "dep_next", "ret_prev", "ret_next"])
    
    # =========================
    # Handlers de administración con FSM
    # =========================
    dp.message.register(procesar_user_id, AdminStates.waiting_for_user_id)
    dp.message.register(procesar_cantidad_admin, AdminStates.waiting_for_amount)
    dp.message.register(procesar_razon_admin, AdminStates.waiting_for_reason)
    
    # =========================
    # Botones de menú
    # =========================
    dp.message.register(referidos_handler, lambda m: m.text and "Referidos" in m.text)
    dp.message.register(tienda_handler, lambda m: m.text and "Tienda" in m.text)
    dp.message.register(wallet_handler, lambda m: m.text and "Wallet" in m.text)
    dp.message.register(explorar_handler, lambda m: m.text and "Explorar" in m.text)
    dp.message.register(inventario_handler, lambda m: m.text and "Inventario" in m.text)
    dp.message.register(procesar_hash_deposito, WalletStates.waiting_for_deposit_hash)
    register_tienda_handlers(dp)