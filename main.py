import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from modules.commands import register_commands

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN no encontrado en variables de entorno")
    exit(1)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Registrar comandos
register_commands(dp)

async def on_startup(dispatcher):
    """Evento de inicio del bot"""
    logger.info("Bot iniciado correctamente")

async def on_shutdown(dispatcher):
    """Evento de cierre del bot"""
    logger.info("Bot cerrado correctamente")

if __name__ == "__main__":
    # Ejecutar bot usando polling
    import asyncio
    asyncio.run(dp.start_polling(bot))
