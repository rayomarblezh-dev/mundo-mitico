import asyncio
from utils.logging_config import setup_logging, get_logger
from utils.database import init_db
from modules.commands import register_commands
from modules.bot import bot, dp
import time

# Configurar logging
setup_logging()
logger = get_logger(__name__)

async def main():
    """Función principal para ejecutar el bot"""
    try:
        logger.info("🚀 Iniciando bot Mundo Mítico...")
        
        # Inicializar base de datos
        await init_db()
        logger.info("✅ Base de datos inicializada correctamente")
        
        # Registrar comandos
        register_commands(dp)
        logger.info("✅ Comandos registrados correctamente")
        
        # Iniciar el bot
        logger.info("🤖 Iniciando bot de Telegram...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Error iniciando el bot: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
