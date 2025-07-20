from aiogram import Dispatcher
from aiogram.filters import Command
from modules.handlers import (
    start_handler, 
    support_callback_handler, 
    tutorials_callback_handler, 
    referidos_handler, 
    tienda_handler,
    tienda_heroes_handler,
    tienda_criaturas_handler,
    heroe_kael_umbros_handler,
    heroe_malrith_handler,
    criatura_hada_handler,
    criatura_elfo_handler,
    criatura_dragon_handler,
    criatura_orco_handler,
    criatura_gremnli_handler,
    criatura_unicornio_handler,
    criatura_genio_handler,
    criatura_kraken_handler,
    criatura_licantropo_handler,
    wallet_handler,
    wallet_depositar_handler,
    wallet_retirar_handler,
    tienda_volver_handler
)

def register_commands(dp: Dispatcher):
    """
    Registrar todos los comandos del bot
    """
    # Comando start
    dp.message.register(start_handler, Command("start"))
    
    # Callbacks
    dp.callback_query.register(support_callback_handler, lambda c: c.data == "support")
    dp.callback_query.register(tutorials_callback_handler, lambda c: c.data == "tutorials")
    dp.callback_query.register(tienda_heroes_handler, lambda c: c.data == "tienda_heroes")
    dp.callback_query.register(tienda_criaturas_handler, lambda c: c.data == "tienda_criaturas")
    dp.callback_query.register(tienda_volver_handler, lambda c: c.data == "tienda_volver")
    dp.callback_query.register(heroe_kael_umbros_handler, lambda c: c.data == "heroe_kael_umbros")
    dp.callback_query.register(heroe_malrith_handler, lambda c: c.data == "heroe_malrith")
    dp.callback_query.register(criatura_hada_handler, lambda c: c.data == "criatura_hada")
    dp.callback_query.register(criatura_elfo_handler, lambda c: c.data == "criatura_elfo")
    dp.callback_query.register(criatura_dragon_handler, lambda c: c.data == "criatura_dragon")
    dp.callback_query.register(criatura_orco_handler, lambda c: c.data == "criatura_orco")
    dp.callback_query.register(criatura_gremnli_handler, lambda c: c.data == "criatura_gremnli")
    dp.callback_query.register(criatura_unicornio_handler, lambda c: c.data == "criatura_unicornio")
    dp.callback_query.register(criatura_genio_handler, lambda c: c.data == "criatura_genio")
    dp.callback_query.register(criatura_kraken_handler, lambda c: c.data == "criatura_kraken")
    dp.callback_query.register(criatura_licantropo_handler, lambda c: c.data == "criatura_licantropo")
    dp.callback_query.register(wallet_depositar_handler, lambda c: c.data == "wallet_depositar")
    dp.callback_query.register(wallet_retirar_handler, lambda c: c.data == "wallet_retirar")
    
    # Botones de menú
    dp.message.register(referidos_handler, lambda m: m.text and "Referidos" in m.text)
    dp.message.register(tienda_handler, lambda m: m.text and "Tienda" in m.text)
    dp.message.register(wallet_handler, lambda m: m.text and "Wallet" in m.text)
    