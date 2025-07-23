import os
import logging
from aiogram import Bot, Dispatcher
from modules.commands import register_commands
from utils.database import init_db, usuarios_col
from modules.bot import bot, dp
import datetime
from aiogram.types import FSInputFile
import collections
from config.config import BOT_TOKEN

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar bot
if not BOT_TOKEN:
    logger.error("BOT_TOKEN no encontrado. Configura tu token en el código.")
    exit(1)

# Registrar comandos
register_commands(dp)

# Eliminar importaciones relacionadas con captcha, Pillow y qrcode

MUNDO_MITICO_VARIANTS = [
    "mundo mitico", "mundomitico", "mundo mítico", "mundomítico"
]

def contiene_mundo_mitico(nombre):
    nombre = nombre.lower()
    return any(variant in nombre for variant in MUNDO_MITICO_VARIANTS)

# Eliminar uso de CaptchaMiddleware y generar_captcha_imagen

from aiogram.dispatcher.middlewares.base import BaseMiddleware
class MundoMiticoNombreMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, 'from_user', None)
        if user:
            nombre_usuario = (getattr(user, 'first_name', '') or '') + ' ' + (getattr(user, 'username', '') or '')
            if contiene_mundo_mitico(nombre_usuario):
                logger.info(f"[MUNDO_MITICO] Usuario {user.id} tiene 'Mundo Mitico' en su nombre: {nombre_usuario}")
                # Guardar registro en la base de datos
                await usuarios_col.update_one(
                    {"user_id": user.id},
                    {"$set": {"detectado_mundo_mitico": True, "nombre_detectado": nombre_usuario, "fecha_detectado": datetime.datetime.now()}},
                    upsert=True
                )
                # Notificar al usuario (si es un mensaje o callback)
                if hasattr(event, 'answer'):
                    try:
                        await event.answer("🎉 ¡Tu nombre contiene 'Mundo Mitico'!", show_alert=True)
                    except Exception:
                        pass
                elif hasattr(event, 'message'):
                    try:
                        await event.message.answer("🎉 ¡Tu nombre contiene 'Mundo Mitico'!")
                    except Exception:
                        pass
        return await handler(event, data)

dp.update.outer_middleware(MundoMiticoNombreMiddleware())

# Nueva función main para aiogram v3
async def main():
    await init_db()
    logger.info("Bot iniciado correctamente")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
