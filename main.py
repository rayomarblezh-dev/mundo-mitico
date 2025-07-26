import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from utils.logging_config import setup_logging, get_logger
from utils.database import init_db
from modules.commands import register_commands
from modules.bot import bot, dp

# Configurar logging
setup_logging()
logger = get_logger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Mundo Mítico Bot API",
    description="API para el bot de Telegram Mundo Mítico",
    version="1.0.0"
)

# Variable global para el estado del bot
bot_running = False
bot_task = None

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    global bot_running, bot_task
    
    try:
        logger.info("🚀 Iniciando aplicación Mundo Mítico...")
        
        # Inicializar base de datos
        await init_db()
        logger.info("✅ Base de datos inicializada correctamente")
        
        # Registrar comandos
        register_commands(dp)
        logger.info("✅ Comandos registrados correctamente")
        
        # Iniciar el bot en segundo plano
        bot_task = asyncio.create_task(start_bot())
        bot_running = True
        
        logger.info("✅ Bot iniciado correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error iniciando la aplicación: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicación"""
    global bot_running, bot_task
    
    logger.info("🛑 Cerrando aplicación Mundo Mítico...")
    
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    
    bot_running = False
    logger.info("✅ Aplicación cerrada correctamente")

async def start_bot():
    """Función para iniciar el bot en segundo plano"""
    try:
        logger.info("🤖 Iniciando bot de Telegram...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Error en el bot: {e}")
        bot_running = False

# Endpoints de la API

@app.get("/")
async def root():
    """Endpoint raíz con información del bot"""
    return {
        "message": "Mundo Mítico Bot API",
        "status": "running" if bot_running else "stopped",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    try:
        # Verificar que el bot esté funcionando
        if not bot_running:
            raise HTTPException(status_code=503, detail="Bot no está ejecutándose")
        
        # Verificar conexión a la base de datos
        from utils.database import client
        await client.admin.command('ping')
        
        return {
            "status": "healthy",
            "bot_running": bot_running,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/status")
async def bot_status():
    """Endpoint para obtener el estado del bot"""
    return {
        "bot_running": bot_running,
        "bot_info": {
            "username": bot.username if bot.username else "Unknown",
            "id": bot.id if bot.id else "Unknown"
        }
    }

@app.post("/restart")
async def restart_bot():
    """Endpoint para reiniciar el bot (solo para admins)"""
    global bot_running, bot_task
    
    try:
        logger.info("🔄 Reiniciando bot...")
        
        # Detener el bot actual
        if bot_task:
            bot_task.cancel()
            try:
                await bot_task
            except asyncio.CancelledError:
                pass
        
        # Iniciar nuevo bot
        bot_task = asyncio.create_task(start_bot())
        bot_running = True
        
        logger.info("✅ Bot reiniciado correctamente")
        
        return {"message": "Bot reiniciado correctamente", "status": "success"}
        
    except Exception as e:
        logger.error(f"❌ Error reiniciando bot: {e}")
        raise HTTPException(status_code=500, detail=f"Error reiniciando bot: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Endpoint para obtener estadísticas del sistema"""
    try:
        from utils.database import obtener_estadisticas_generales, obtener_usuarios_activos
        
        stats = await obtener_estadisticas_generales()
        usuarios_activos = await obtener_usuarios_activos(7)
        
        return {
            "total_usuarios": stats.get('total_usuarios', 0),
            "total_depositos": stats.get('total_depositos', 0),
            "total_retiros": stats.get('total_retiros', 0),
            "volumen_total": stats.get('volumen_total', 0),
            "usuarios_activos_7d": usuarios_activos,
            "bot_running": bot_running
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

# Manejo de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    # Configuración para desarrollo local
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443,
        reload=False,
        log_level="info"
    )
