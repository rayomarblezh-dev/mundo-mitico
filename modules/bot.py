import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import BOT_TOKEN, is_admin
from modules.tareas import MundoMiticoNombreMiddleware
from aiogram.dispatcher.middlewares.base import BaseMiddleware

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Verificar BOT_TOKEN
if not BOT_TOKEN:
    logger.critical("❌ BOT_TOKEN no encontrado en variables de entorno. El bot se detendrá.")
    exit(1)

# Inicialización del bot y dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class RestriccionPorTipoUsuarioMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, 'from_user', None)
        if not user:
            return await handler(event, data)
        es_admin = is_admin(user.id)

        # Restricción de comandos para mensajes
        if hasattr(event, 'text'):
            texto = (event.text or "").strip()
            if es_admin:
                if not (texto.startswith("/admin") or texto.startswith("/info")):
                    await event.answer("❌ Como administrador solo puedes usar /admin y /info.", show_alert=True)
                    return
            else:
                if texto.startswith("/admin"):
                    await event.answer("❌ Comando reservado solo para administradores.", show_alert=True)
                    return

        # Restricción de callbacks
        if hasattr(event, 'data'):
            data_cb = (event.data or "").strip()
            if es_admin:
                if not (data_cb == "admin" or data_cb.startswith("admin_") or data_cb == "info"):
                    await event.answer("❌ Solo puedes usar el panel de administración.", show_alert=True)
                    return
            else:
                if data_cb == "admin" or data_cb.startswith("admin_"):
                    await event.answer("❌ Función exclusiva para administradores.", show_alert=True)
                    return

        return await handler(event, data)

# Registro de middlewares
dp.update.outer_middleware(RestriccionPorTipoUsuarioMiddleware())
dp.update.outer_middleware(MundoMiticoNombreMiddleware())