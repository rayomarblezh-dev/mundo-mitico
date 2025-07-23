# =========================
# Importaciones
# =========================
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import es_elegible_paquete_bienvenida, PAQUETE_PRECIO, registrar_compra_paquete_bienvenida, usuario_compro_paquete_bienvenida

from modules.start import start_handler
from modules.guia import guia_callback_handler
from modules.referidos import referidos_handler
from modules.tienda import (
    tienda_handler,
    tienda_criaturas_handler,
    tienda_volver_handler
)

from modules.criaturas import (
    criatura_hada_handler,
    criatura_elfo_handler,
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
    admin_agregar_credito_handler,
    procesar_user_id,
    procesar_cantidad_admin,
    procesar_razon_admin,
    confirmar_credito_handler,
    cancelar_credito_handler,
    admin_estadisticas_handler,
    admin_depositos_handler,
    admin_config_handler,
    AdminStates,
    info_handler
)


# =========================
# Registro de comandos
# =========================
async def mostrar_promo_paquete_bienvenida(message, user_id):
    if await es_elegible_paquete_bienvenida(user_id):
        promo_text = (
            '💎 <b>¡Paquete de bienvenida!</b>\n'
            '7 🧚 Hadas, 3 🧙 Magos, 1 🐺 Licántropo por solo <b>1.5 TON</b>.'
            '\n<i>Solo por 15 días desde este registro.</i>'
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Comprar Ahora!", callback_data="comprar_paquete_bienvenida")]
            ]
        )
        await message.answer(promo_text, parse_mode="HTML", reply_markup=keyboard)

# Handler para el botón Comprar del paquete de bienvenida
from aiogram import types
from utils.database import obtener_balance_usuario, agregar_credito_usuario

async def comprar_paquete_bienvenida_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = await obtener_balance_usuario(user_id)
    if not await es_elegible_paquete_bienvenida(user_id):
        await callback.answer("La promoción ya no está disponible.", show_alert=True)
        return
    if balance < PAQUETE_PRECIO:
        await callback.answer("No tienes suficiente TON para comprar el paquete.", show_alert=True)
        return
    # Descontar TON
    await agregar_credito_usuario(user_id, -PAQUETE_PRECIO, "Paquete de bienvenida", admin_id=0)
    await registrar_compra_paquete_bienvenida(user_id)
    await callback.message.answer(
        "🎉 <b>¡Has comprado el paquete de bienvenida!</b>\nLas criaturas han sido añadidas a tu inventario.",
        parse_mode="HTML"
    )
    await callback.answer()

def register_commands(dp: Dispatcher):
    """
    Registrar todos los comandos del bot
    """

    # =========================
    # Comando /start
    # =========================
    dp.message.register(start_handler, Command("start"))
    
    # =========================
    # Comando /admin
    # =========================
    dp.message.register(admin_handler, Command("admin"))
    
    # =========================
    # Comando /info
    # =========================
    dp.message.register(info_handler, Command("info"))
    
    # =========================
    # Callbacks de guia
    # =========================
    dp.callback_query.register(guia_callback_handler, lambda c: c.data == "guia")

    # =========================
    # Callbacks de tienda
    # =========================
    dp.callback_query.register(tienda_criaturas_handler, lambda c: c.data == "tienda_criaturas")
    dp.callback_query.register(tienda_volver_handler, lambda c: c.data == "tienda_volver")
    dp.callback_query.register(nfts_handler, lambda c: c.data == "tienda_nfts")
    
    # =========================
    # Callbacks de criaturas
    # =========================
    dp.callback_query.register(criatura_hada_handler, lambda c: c.data == "criatura_hada")
    dp.callback_query.register(criatura_elfo_handler, lambda c: c.data == "criatura_elfo")
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
    # Handlers para confirmar/cancelar retiro
    dp.callback_query.register(confirmar_retiro_handler, lambda c: c.data == "confirmar_retiro")
    dp.callback_query.register(cancelar_retiro_handler, lambda c: c.data == "cancelar_retiro")
    
    # =========================
    # Callbacks de administración
    # =========================
    dp.callback_query.register(admin_agregar_credito_handler, lambda c: c.data == "admin_agregar_credito")
    dp.callback_query.register(confirmar_credito_handler, lambda c: c.data == "admin_confirmar_credito")
    dp.callback_query.register(cancelar_credito_handler, lambda c: c.data == "admin_cancelar_credito")
    dp.callback_query.register(admin_estadisticas_handler, lambda c: c.data == "admin_estadisticas")
    dp.callback_query.register(admin_depositos_handler, lambda c: c.data == "admin_depositos")
    dp.callback_query.register(admin_config_handler, lambda c: c.data == "admin_config")
    dp.callback_query.register(comprar_paquete_bienvenida_handler, lambda c: c.data == "comprar_paquete_bienvenida")
    
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
    dp.message.register(procesar_hash_deposito, WalletStates.waiting_for_deposit_hash)