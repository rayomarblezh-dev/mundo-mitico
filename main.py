import asyncio
import logging
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from utils.logging_config import setup_logging, get_logger
from utils.database import init_db
from modules.commands import register_commands
from modules.bot import bot, dp
from config.config import API_HOST, API_PORT, API_WORKERS

# Importar Flask app del panel de administración
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'admin_panel'))

# Importación condicional para evitar errores si no está instalado Flask
try:
    from app import app as flask_app
    FLASK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Flask no disponible: {e}")
    FLASK_AVAILABLE = False
    flask_app = None

# Configurar logging
setup_logging()
logger = get_logger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Mundo Mítico Bot API",
    description="API para el bot de Telegram Mundo Mítico",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para el panel de administración
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        
        # Iniciar Flask en un hilo separado
        if FLASK_AVAILABLE:
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            logger.info("✅ Panel de administración iniciado en http://localhost:5001")
        else:
            logger.warning("⚠️ Panel de administración no disponible (Flask no instalado)")
        
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

# =========================
# ENDPOINTS DE LA API
# =========================

def run_flask():
    """Función para ejecutar Flask en un hilo separado"""
    if not FLASK_AVAILABLE:
        print("❌ Flask no disponible, no se puede iniciar el panel de administración")
        return
    
    try:
        # En Railway, usar la variable PORT que asigna automáticamente
        port = int(os.environ.get('PORT', 5001))
        flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error iniciando Flask: {e}")

@app.get("/")
async def root():
    """Endpoint raíz con información del bot"""
    return {
        "message": "Mundo Mítico Bot API",
        "status": "running" if bot_running else "stopped",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "admin_panel": "http://localhost:5001" if FLASK_AVAILABLE else "no disponible",
        "admin_panel_url": "http://localhost:5001" if FLASK_AVAILABLE else None
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
            "database": "connected",
            "timestamp": asyncio.get_event_loop().time()
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
        },
        "uptime": asyncio.get_event_loop().time() if bot_running else 0
    }

@app.get("/admin-panel-url")
async def get_admin_panel_url():
    """Endpoint para obtener la URL del panel de administración"""
    if not FLASK_AVAILABLE:
        raise HTTPException(status_code=404, detail="Panel de administración no disponible")
    
    # Intentar obtener la URL desde la configuración del panel
    try:
        from admin_panel.config import PANEL_URL
        admin_url = PANEL_URL
    except ImportError:
        # Si no se puede importar, usar URL por defecto
        admin_url = "http://localhost:5001"
    
    return {
        "admin_panel_url": admin_url,
        "status": "available"
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
            "bot_running": bot_running,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@app.get("/info")
async def get_info():
    """Endpoint para obtener información del sistema"""
    return {
        "app_name": "Mundo Mítico Bot",
        "version": "1.0.0",
        "environment": "production",
        "api_host": API_HOST,
        "api_port": API_PORT,
        "api_workers": API_WORKERS,
        "bot_running": bot_running
    }

# =========================
# MANEJO DE ERRORES GLOBAL
# =========================

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
        host=API_HOST,
        port=API_PORT,
        workers=API_WORKERS,
        reload=False,
        log_level="info"
    )
