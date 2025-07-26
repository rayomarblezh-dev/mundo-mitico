from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config.config import BOT_TOKEN
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Configurar el bot con manejo de errores mejorado
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

# Configurar el dispatcher con storage en memoria
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

logger.info("🤖 Bot y Dispatcher configurados correctamente")