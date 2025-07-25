import logging
from modules.commands import register_commands
from utils.database import init_db
from config.config import BOT_TOKEN
from modules.bot import bot, dp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar bot
if not BOT_TOKEN:
    logger.error("BOT_TOKEN no encontrado. Configura tu token en el código.")
    exit(1)

# Registrar comandos
register_commands(dp)

# Nueva función main para aiogram v3
async def main():
    await init_db()
    logger.info("Bot iniciado correctamente")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
