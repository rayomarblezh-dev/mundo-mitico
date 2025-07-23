import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from modules.commands import register_commands
from utils.database import init_db
from modules.bot import bot, dp
from modules.captcha import generar_captcha_qr
from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

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

# Registrar comandos
register_commands(dp)

# Middleware para captcha
class CaptchaMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id if hasattr(event, 'from_user') else None
        # Aquí deberías verificar si el usuario es nuevo (ejemplo simple)
        if user_id and not await usuario_ya_verificado(user_id):
            path_qr, numeros = generar_captcha_qr()
            await event.answer_photo(open(path_qr, 'rb'), caption="Por favor, introduce los 6 números que ves en el QR para continuar.")
            # Aquí deberías esperar la respuesta y validarla antes de continuar
            # ... lógica de validación ...
            return  # No continúa hasta que pase el captcha
        return await handler(event, data)

def usuario_ya_verificado(user_id):
    # Aquí deberías consultar tu base de datos para saber si el usuario ya pasó el captcha
    return False  # Por ahora, todos pasan por el captcha

dp.update.outer_middleware(CaptchaMiddleware())

async def on_startup(dispatcher):
    """Evento de inicio del bot"""
    await init_db()
    logger.info("Bot iniciado correctamente")

async def on_shutdown(dispatcher):
    """Evento de cierre del bot"""
    logger.info("Bot cerrado correctamente")

if __name__ == "__main__":
    # Ejecutar bot usando polling
    import asyncio
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
