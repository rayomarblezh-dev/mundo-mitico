import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import BOT_TOKEN

# Cargar variables de entorno

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar bot
if not BOT_TOKEN:
    logger.error("BOT_TOKEN no encontrado en variables de entorno")
    exit(1)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage) 