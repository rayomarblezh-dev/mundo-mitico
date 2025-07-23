import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import BOT_TOKEN
from config.config import is_admin

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

# Middleware para restringir comandos y callbacks según el tipo de usuario
from aiogram.dispatcher.middlewares.base import BaseMiddleware
class RestriccionPorTipoUsuarioMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, 'from_user', None)
        if not user:
            return await handler(event, data)
        es_admin = is_admin(user.id)
        # Mensajes
        if hasattr(event, 'text'):
            texto = event.text or ""
            if es_admin:
                if not (texto.startswith("/admin") or texto.startswith("/info")):
                    await event.answer("❌ Solo puedes usar /admin y /info como admin.", show_alert=True)
                    return
            else:
                if texto.startswith("/admin"):
                    await event.answer("❌ Comando no permitido.", show_alert=True)
                    return
        # Callbacks
        if hasattr(event, 'data'):
            data_cb = event.data or ""
            if es_admin:
                if not (data_cb == "admin" or data_cb.startswith("admin_") or data_cb == "info"):
                    await event.answer("❌ Solo puedes usar el panel de administración.", show_alert=True)
                    return
            else:
                if data_cb == "admin" or data_cb.startswith("admin_"):
                    await event.answer("❌ Función solo para administradores.", show_alert=True)
                    return
        return await handler(event, data)

dp.update.outer_middleware(RestriccionPorTipoUsuarioMiddleware()) 