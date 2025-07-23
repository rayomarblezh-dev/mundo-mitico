import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from modules.commands import register_commands
from utils.database import init_db, usuarios_col
from modules.bot import bot, dp
from modules.captcha import generar_captcha_qr, generar_teclado_captcha
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
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

# Diccionario temporal para almacenar el progreso del captcha (por usuario)
captcha_progreso = {}

class CaptchaMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id if hasattr(event, 'from_user') else None
        if not user_id:
            return await handler(event, data)
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            # Crear usuario si no existe
            await usuarios_col.insert_one({"user_id": user_id, "captcha": {"verificado": False, "codigo": None, "progreso": ""}})
            usuario = await usuarios_col.find_one({"user_id": user_id})
        captcha = usuario.get("captcha", {"verificado": False, "codigo": None, "progreso": ""})
        if captcha.get("verificado"):
            return await handler(event, data)
        # Si el usuario no ha pasado el captcha
        # Si es un callback de botón de captcha
        if isinstance(event, CallbackQuery) and event.data and event.data.startswith("captcha_"):
            digito = event.data.replace("captcha_", "")
            progreso = captcha.get("progreso", "") + digito
            # Actualizar progreso en la base de datos
            await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.progreso": progreso}})
            # Obtener el código correcto
            codigo = captcha.get("codigo")
            if not codigo:
                await event.answer("Error interno. Vuelve a intentarlo.", show_alert=True)
                raise CancelHandler()
            if len(progreso) < 6:
                await event.message.edit_reply_markup(reply_markup=generar_teclado_captcha())
                await event.answer(f"Has ingresado: {progreso}")
                raise CancelHandler()
            if progreso == codigo:
                await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.verificado": True, "captcha.progreso": ""}})
                await event.message.edit_caption("✅ Captcha verificado correctamente. ¡Bienvenido!", reply_markup=None)
                await event.answer("¡Correcto!")
                return await handler(event, data)
            else:
                # Reiniciar captcha
                await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.progreso": ""}})
                await event.message.edit_caption("❌ Código incorrecto. Intenta de nuevo.")
                await event.message.edit_reply_markup(reply_markup=generar_teclado_captcha())
                await event.answer("Código incorrecto. Intenta de nuevo.")
                raise CancelHandler()
        # Si no hay captcha generado, generarlo y enviar QR
        if not captcha.get("codigo"):
            path_qr, numeros = generar_captcha_qr()
            await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.codigo": numeros, "captcha.progreso": ""}})
            with open(path_qr, 'rb') as photo:
                await event.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
            raise CancelHandler()
        # Si hay captcha pendiente, mostrar QR y teclado
        if not captcha.get("verificado"):
            codigo = captcha.get('codigo')
            path_qr = os.path.join('images', f'captcha_{codigo}.png')
            if os.path.exists(path_qr):
                with open(path_qr, 'rb') as photo:
                    await event.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
            else:
                # Si no existe el QR, regenerar
                path_qr, numeros = generar_captcha_qr()
                await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.codigo": numeros, "captcha.progreso": ""}})
                with open(path_qr, 'rb') as photo:
                    await event.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
            raise CancelHandler()
        return await handler(event, data)

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
