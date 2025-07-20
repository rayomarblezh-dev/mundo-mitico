from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import threading
import os
import logging
import uvicorn
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable global para el cliente HTTP
http_client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global http_client
    
    # Startup
    http_client = httpx.AsyncClient(timeout=30.0)
    
    # Ejecutar bot en hilo separado
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    logger.info("API iniciada correctamente")
    
    yield
    
    # Shutdown
    if http_client:
        await http_client.aclose()
    
    logger.info("API cerrada correctamente")

app = FastAPI(
    title="Mundo Mítico API",
    description="API para el bot de Telegram Mundo Mítico",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root() -> Dict[str, str]:
    """Endpoint principal de la API"""
    return {"message": "API Mundo Mítico online", "status": "active"}

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy",
        "service": "mundo-mitico-api",
        "version": "1.0.0"
    }



def run_bot():
    """Ejecutar el bot de Telegram"""
    try:
        logger.info("Iniciando bot de Telegram...")
        # Importar y ejecutar el bot directamente
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from main import bot, dp
        import asyncio
        
        # Ejecutar el bot en el hilo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(dp.start_polling(bot))
        
    except Exception as e:
        logger.error(f"Error al ejecutar el bot: {e}")

# Función de utilidad para hacer peticiones HTTP
async def make_http_request(url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
    """Realizar petición HTTP usando httpx"""
    if not http_client:
        raise HTTPException(status_code=500, detail="Cliente HTTP no inicializado")
    
    try:
        response = await http_client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError as e:
        logger.error(f"Error de conexión: {e}")
        raise HTTPException(status_code=503, detail="Error de conexión")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    # Ejecutar con uvicorn
    uvicorn.run(
        "FastAPI:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )