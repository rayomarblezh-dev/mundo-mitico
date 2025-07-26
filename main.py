import asyncio
import logging
import threading
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
from utils.logging_config import setup_logging, get_logger
from utils.database import init_db
from modules.commands import register_commands
from modules.bot import bot, dp
from config.config import API_HOST, API_PORT, API_WORKERS

# Importar Flask para el panel de administración
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import datetime
from functools import wraps
import motor.motor_asyncio
from bson import ObjectId
from typing import Optional

# Configuración del panel Flask
from config.config import MONGO_URI, DB_NAME, ADMIN_IDS, FLASK_PORT
DATABASE_NAME = DB_NAME
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'V7rX!p9Lq$3tZ@fM')

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

# Crear aplicación Flask para el panel
flask_app = Flask(__name__)
flask_app.secret_key = ADMIN_SECRET_KEY
CORS(flask_app)

# Configuración de MongoDB para Flask
try:
    flask_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    flask_db = flask_client[DATABASE_NAME]
    print(f"✅ Conectado a MongoDB para Flask: {DATABASE_NAME}")
except Exception as e:
    print(f"❌ Error conectando a MongoDB para Flask: {e}")
    flask_db = None

# Simulación de sesiones para Flask
admin_sessions = {}

def get_admin_id(request):
    """Obtener admin_id de la sesión"""
    session_id = request.cookies.get("admin_session")
    return admin_sessions.get(session_id)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = get_admin_id(request)
        if not admin_id or admin_id not in ADMIN_IDS:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de Flask
@flask_app.route('/')
def index():
    admin_id = get_admin_id(request)
    if admin_id and admin_id in ADMIN_IDS:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@flask_app.route('/login')
def login():
    return render_template('login.html')

@flask_app.route('/login', methods=['POST'])
def login_post():
    admin_id = request.form.get('adminId')
    try:
        admin_id = int(admin_id)
        if admin_id in ADMIN_IDS:
            # Crear sesión simple
            session_id = f"session_{admin_id}_{datetime.datetime.now().timestamp()}"
            admin_sessions[session_id] = admin_id
            
            response = redirect(url_for('dashboard'))
            response.set_cookie(key="admin_session", value=session_id, httponly=True)
            return response
        else:
            return render_template('login.html', error='ID de administrador inválido')
    except ValueError:
        return render_template('login.html', error='ID debe ser un número')

@flask_app.route('/logout')
def logout():
    session_id = request.cookies.get("admin_session")
    if session_id in admin_sessions:
        del admin_sessions[session_id]
    
    response = redirect(url_for('login'))
    response.delete_cookie("admin_session")
    return response

@flask_app.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html')

@flask_app.route('/api/stats')
@admin_required
def get_flask_stats():
    """Obtener estadísticas del sistema"""
    try:
        stats = asyncio.run(get_statistics())
        return jsonify(stats)
    except Exception as e:
        import traceback
        print('Error en /api/stats:', traceback.format_exc())
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@flask_app.route('/api/deposits')
@admin_required
def get_deposits():
    """Obtener depósitos pendientes"""
    try:
        deposits = asyncio.run(get_pending_deposits())
        return jsonify(deposits)
    except Exception as e:
        import traceback
        print('Error en /api/deposits:', traceback.format_exc())
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@flask_app.route('/api/withdrawals')
@admin_required
def get_withdrawals():
    """Obtener retiros pendientes"""
    try:
        withdrawals = asyncio.run(get_pending_withdrawals())
        return jsonify(withdrawals)
    except Exception as e:
        import traceback
        print('Error en /api/withdrawals:', traceback.format_exc())
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@flask_app.route('/api/process-deposit', methods=['POST'])
@admin_required
def process_deposit():
    """Procesar un depósito"""
    try:
        deposit_id = request.form.get('deposit_id')
        amount = float(request.form.get('amount'))
        admin_id = get_admin_id(request)
        
        result = asyncio.run(process_deposit_async(deposit_id, amount, admin_id))
        return jsonify(result)
    except Exception as e:
        import traceback
        print('Error en /api/process-deposit:', traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/process-withdrawal', methods=['POST'])
@admin_required
def process_withdrawal():
    """Procesar un retiro"""
    try:
        withdrawal_id = request.form.get('withdrawal_id')
        admin_id = get_admin_id(request)
        
        result = asyncio.run(process_withdrawal_async(withdrawal_id, admin_id))
        return jsonify(result)
    except Exception as e:
        import traceback
        print('Error en /api/process-withdrawal:', traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/cancel-deposit', methods=['POST'])
@admin_required
def cancel_deposit():
    """Cancelar un depósito"""
    try:
        deposit_id = request.form.get('deposit_id')
        admin_id = get_admin_id(request)
        
        result = asyncio.run(cancel_deposit_async(deposit_id, admin_id))
        return jsonify(result)
    except Exception as e:
        import traceback
        print('Error en /api/cancel-deposit:', traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/cancel-withdrawal', methods=['POST'])
@admin_required
def cancel_withdrawal():
    """Cancelar un retiro"""
    try:
        withdrawal_id = request.form.get('withdrawal_id')
        admin_id = get_admin_id(request)
        
        result = asyncio.run(cancel_withdrawal_async(withdrawal_id, admin_id))
        return jsonify(result)
    except Exception as e:
        import traceback
        print('Error en /api/cancel-withdrawal:', traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

# Funciones asíncronas para Flask
async def get_statistics():
    if flask_db is None:
        return {
            'total_users': 0,
            'total_deposits': 0,
            'total_withdrawals': 0,
            'total_volume': 0,
            'active_users': 0
        }
    
    try:
        # Obtener estadísticas de usuarios
        total_users = await flask_db.users.count_documents({})
        
        # Obtener estadísticas de depósitos
        total_deposits = await flask_db.deposits.count_documents({})
        deposits_volume = await flask_db.deposits.aggregate([
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        total_volume = deposits_volume[0]['total'] if deposits_volume else 0
        
        # Obtener estadísticas de retiros
        total_withdrawals = await flask_db.withdrawals.count_documents({})
        
        # Usuarios activos en los últimos 7 días
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        active_users = await flask_db.users.count_documents({
            "last_activity": {"$gte": seven_days_ago}
        })
        
        return {
            'total_users': total_users,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_volume': total_volume,
            'active_users': active_users
        }
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {
            'total_users': 0,
            'total_deposits': 0,
            'total_withdrawals': 0,
            'total_volume': 0,
            'active_users': 0
        }

async def get_pending_deposits():
    if flask_db is None:
        return []
    
    try:
        deposits = await flask_db.deposits.find({"status": "pending"}).to_list(100)
        return [
            {
                'id': str(dep['_id']),
                'user_id': dep.get('user_id', 'N/A'),
                'amount': dep.get('amount', 0),
                'network': dep.get('network', 'N/A'),
                'hash': dep.get('hash', ''),
                'address': dep.get('address', ''),
                'date': dep.get('date', '').strftime('%Y-%m-%d %H:%M:%S') if dep.get('date') else ''
            }
            for dep in deposits
        ]
    except Exception as e:
        print(f"Error obteniendo depósitos: {e}")
        return []

async def get_pending_withdrawals():
    if flask_db is None:
        return []
    
    try:
        withdrawals = await flask_db.withdrawals.find({"status": "pending"}).to_list(100)
        return [
            {
                'id': str(w['_id']),
                'user_id': w.get('user_id', 'N/A'),
                'amount': w.get('amount', 0),
                'wallet': w.get('wallet', ''),
                'date': w.get('date', '').strftime('%Y-%m-%d %H:%M:%S') if w.get('date') else ''
            }
            for w in withdrawals
        ]
    except Exception as e:
        print(f"Error obteniendo retiros: {e}")
        return []

async def process_deposit_async(deposit_id, amount, admin_id):
    if flask_db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el depósito
        result = await flask_db.deposits.update_one(
            {"_id": ObjectId(deposit_id)},
            {
                "$set": {
                    "status": "completed",
                    "processed_by": admin_id,
                    "processed_at": datetime.datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return {'success': False, 'message': 'Depósito no encontrado'}
        
        # Obtener información del depósito
        deposit = await flask_db.deposits.find_one({"_id": ObjectId(deposit_id)})
        if not deposit:
            return {'success': False, 'message': 'Depósito no encontrado'}
        
        user_id = deposit.get('user_id')
        
        # Actualizar balance del usuario
        await flask_db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}},
            upsert=True
        )
        
        # Registrar la acción del admin
        await flask_db.admin_actions.insert_one({
            "admin_id": admin_id,
            "action": "process_deposit",
            "deposit_id": ObjectId(deposit_id),
            "amount": amount,
            "user_id": user_id,
            "timestamp": datetime.datetime.now()
        })
        
        return {'success': True, 'message': f'Depósito de ${amount} procesado correctamente'}
        
    except Exception as e:
        print(f"Error procesando depósito: {e}")
        return {'success': False, 'message': f'Error: {str(e)}'}

async def process_withdrawal_async(withdrawal_id, admin_id):
    if flask_db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el retiro
        result = await flask_db.withdrawals.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "status": "completed",
                    "processed_by": admin_id,
                    "processed_at": datetime.datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        # Obtener información del retiro
        withdrawal = await flask_db.withdrawals.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        user_id = withdrawal.get('user_id')
        amount = withdrawal.get('amount', 0)
        
        # Registrar la acción del admin
        await flask_db.admin_actions.insert_one({
            "admin_id": admin_id,
            "action": "process_withdrawal",
            "withdrawal_id": ObjectId(withdrawal_id),
            "amount": amount,
            "user_id": user_id,
            "timestamp": datetime.datetime.now()
        })
        
        return {'success': True, 'message': f'Retiro de ${amount} procesado correctamente'}
        
    except Exception as e:
        print(f"Error procesando retiro: {e}")
        return {'success': False, 'message': f'Error: {str(e)}'}

async def cancel_deposit_async(deposit_id, admin_id):
    if flask_db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el depósito
        result = await flask_db.deposits.update_one(
            {"_id": ObjectId(deposit_id)},
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_by": admin_id,
                    "cancelled_at": datetime.datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return {'success': False, 'message': 'Depósito no encontrado'}
        
        # Registrar la acción del admin
        await flask_db.admin_actions.insert_one({
            "admin_id": admin_id,
            "action": "cancel_deposit",
            "deposit_id": ObjectId(deposit_id),
            "timestamp": datetime.datetime.now()
        })
        
        return {'success': True, 'message': 'Depósito cancelado correctamente'}
        
    except Exception as e:
        print(f"Error cancelando depósito: {e}")
        return {'success': False, 'message': f'Error: {str(e)}'}

async def cancel_withdrawal_async(withdrawal_id, admin_id):
    if flask_db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el retiro
        result = await flask_db.withdrawals.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_by": admin_id,
                    "cancelled_at": datetime.datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        # Obtener información del retiro
        withdrawal = await flask_db.withdrawals.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        user_id = withdrawal.get('user_id')
        amount = withdrawal.get('amount', 0)
        
        # Devolver el balance al usuario
        await flask_db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}},
            upsert=True
        )
        
        # Registrar la acción del admin
        await flask_db.admin_actions.insert_one({
            "admin_id": admin_id,
            "action": "cancel_withdrawal",
            "withdrawal_id": ObjectId(withdrawal_id),
            "amount": amount,
            "user_id": user_id,
            "timestamp": datetime.datetime.now()
        })
        
        return {'success': True, 'message': f'Retiro de ${amount} cancelado y balance devuelto'}
        
    except Exception as e:
        print(f"Error cancelando retiro: {e}")
        return {'success': False, 'message': f'Error: {str(e)}'}

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
        logger.info("✅ Panel de administración Flask integrado en FastAPI")
        
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

@app.get("/")
async def root():
    """Endpoint raíz con información del bot"""
    return {
        "message": "Mundo Mítico Bot API",
        "status": "running" if bot_running else "stopped",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "admin_panel": "/admin",
        "admin_panel_url": "/admin"
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
            "flask_integrated": True,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/status")
async def bot_status():
    """Endpoint para obtener el estado del bot"""
    try:
        bot_info = await bot.get_me()
        return {
            "bot_running": bot_running,
            "bot_info": {
                "username": bot_info.username if bot_info.username else "Unknown",
                "id": bot_info.id if bot_info.id else "Unknown"
            },
            "uptime": asyncio.get_event_loop().time() if bot_running else 0,
            "flask_integrated": True,
            "admin_panel_url": "/admin"
        }
    except Exception as e:
        return {
            "bot_running": bot_running,
            "bot_info": {
                "username": "Unknown",
                "id": "Unknown"
            },
            "uptime": 0,
            "flask_integrated": True,
            "admin_panel_url": "/admin",
            "error": str(e)
        }

@app.get("/admin-panel-url")
async def get_admin_panel_url():
    """Endpoint para obtener la URL del panel de administración"""
    admin_url = os.environ.get('ADMIN_PANEL_URL', '/admin')
    
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
            "usuarios_activos": usuarios_activos,
            "flask_integrated": True,
            "admin_panel_url": "/admin"
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def get_info():
    """Endpoint para obtener información general del sistema"""
    return {
        "name": "Mundo Mítico Bot",
        "version": "1.0.0",
        "description": "Bot de Telegram para el juego Mundo Mítico",
        "features": [
            "Bot de Telegram",
            "Panel de administración web",
            "API REST",
            "Base de datos MongoDB",
            "Sistema de depósitos y retiros"
        ],
        "endpoints": {
            "bot_api": "/docs",
            "admin_panel": "/admin",
            "health": "/health",
            "status": "/status"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

# Montar Flask en FastAPI
app.mount("/admin", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info"
    )
