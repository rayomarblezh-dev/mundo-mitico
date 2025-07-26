from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import BOT_TOKEN, is_admin
from modules.tareas import MundoMiticoNombreMiddleware
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Verificar BOT_TOKEN
if not BOT_TOKEN:
    logger.critical("❌ BOT_TOKEN no encontrado en variables de entorno. El bot se detendrá.")
    exit(1)

# Inicialización del bot y dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Registro de middlewares
dp.update.outer_middleware(MundoMiticoNombreMiddleware())