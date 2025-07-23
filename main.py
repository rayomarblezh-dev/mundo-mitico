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
import datetime

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

# Diccionario temporal para almacenar el progreso del captcha (por usuario)
captcha_progreso = {}

class CaptchaMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Log de depuración para ver el tipo de evento y si tiene from_user
        logging.info(f"[Captcha][DEBUG] Evento recibido: {type(event)} - from_user: {getattr(event, 'from_user', None)}")
        user_id = event.from_user.id if hasattr(event, 'from_user') and event.from_user else None
        if not user_id:
            logging.info("[Captcha] Evento sin user_id, pasando...")
            return await handler(event, data)
        usuario = await usuarios_col.find_one({"user_id": user_id})
        if not usuario:
            logging.info(f"[Captcha] Usuario nuevo {user_id}, creando en DB...")
            await usuarios_col.insert_one({
                "user_id": user_id,
                "captcha": {"verificado": False, "codigo": None, "progreso": ""},
                "fecha_registro": datetime.datetime.now(),
                "activo": True
            })
            usuario = await usuarios_col.find_one({"user_id": user_id})
        captcha = usuario.get("captcha", {"verificado": False, "codigo": None, "progreso": ""})
        if captcha.get("verificado"):
            logging.info(f"[Captcha] Usuario {user_id} ya verificado, permitiendo acceso.")
            return await handler(event, data)
        from aiogram.types import CallbackQuery
        if isinstance(event, CallbackQuery) and event.data and event.data.startswith("captcha_"):
            digito = event.data.replace("captcha_", "")
            progreso = (captcha.get("progreso") or "") + digito
            await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.progreso": progreso}})
            codigo = captcha.get("codigo")
            if not codigo:
                logging.warning(f"[Captcha] Usuario {user_id} sin código asignado. Regenerando...")
                path_qr, numeros = generar_captcha_qr()
                await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.codigo": numeros, "captcha.progreso": ""}})
                with open(path_qr, 'rb') as photo:
                    await event.message.answer_photo(photo, caption="Error interno. Se ha regenerado el captcha. Intenta de nuevo.", reply_markup=generar_teclado_captcha())
                return
            if len(progreso) < 6:
                await event.message.edit_reply_markup(reply_markup=generar_teclado_captcha())
                await event.answer(f"Has ingresado: {progreso}")
                return
            if progreso == codigo:
                await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.verificado": True, "captcha.progreso": "", "captcha.codigo": None}})
                await event.message.edit_caption("✅ Captcha verificado correctamente. ¡Bienvenido!", reply_markup=None)
                await event.answer("¡Correcto!")
                logging.info(f"[Captcha] Usuario {user_id} pasó el captcha.")
                return await handler(event, data)
            else:
                # Reiniciar captcha
                await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.progreso": ""}})
                await event.message.edit_caption("❌ Código incorrecto. Intenta de nuevo.")
                await event.message.edit_reply_markup(reply_markup=generar_teclado_captcha())
                await event.answer("Código incorrecto. Intenta de nuevo.")
                logging.info(f"[Captcha] Usuario {user_id} falló el captcha. Se reinicia el progreso.")
                return
        # Si no hay captcha generado, generarlo y enviar QR
        if not captcha.get("codigo"):
            path_qr, numeros = generar_captcha_qr()
            await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.codigo": numeros, "captcha.progreso": ""}})
            with open(path_qr, 'rb') as photo:
                await event.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
            logging.info(f"[Captcha] Usuario {user_id} recibe nuevo captcha: {numeros}")
            return
        # Si hay captcha pendiente, mostrar QR y teclado
        if not captcha.get("verificado"):
            codigo = captcha.get('codigo')
            path_qr = os.path.join('images', f'captcha_{codigo}.png')
            if os.path.exists(path_qr):
                with open(path_qr, 'rb') as photo:
                    await event.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
                logging.info(f"[Captcha] Usuario {user_id} reintenta captcha actual: {codigo}")
            else:
                # Si no existe el QR, regenerar
                path_qr, numeros = generar_captcha_qr()
                await usuarios_col.update_one({"user_id": user_id}, {"$set": {"captcha.codigo": numeros, "captcha.progreso": ""}})
                with open(path_qr, 'rb') as photo:
                    await event.answer_photo(photo, caption="Por favor, ingresa el código del QR usando los botones:", reply_markup=generar_teclado_captcha())
                logging.info(f"[Captcha] Usuario {user_id} QR perdido, se regenera: {numeros}")
            return
        return await handler(event, data)

dp.update.outer_middleware(CaptchaMiddleware())

async def on_startup(dispatcher):
    """Evento de inicio del bot"""
    await init_db()
    logger.info("Bot iniciado correctamente")

async def on_shutdown(dispatcher):
    """Evento de cierre del bot"""
    logger.info("Bot cerrado correctamente")

# Nueva función main para aiogram v3
async def main():
    await init_db()
    logger.info("Bot iniciado correctamente")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
