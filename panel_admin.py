#!/usr/bin/env python
"""
Panel de Administración Flask para Mundo Mítico
"""
import asyncio
import json
import os
import motor.motor_asyncio
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from bson import ObjectId

# Cargar variables de entorno
load_dotenv("config.env")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '7828962018').split(',')]
MONGO_URI = os.getenv('MONGO_URI', 'localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'mundomi')
SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', 'V7rX!p9Lq$3tZ@fM')

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

# Cliente MongoDB
def get_mongo_client():
    """Obtiene cliente de MongoDB"""
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=60000,
            connectTimeoutMS=60000,
            socketTimeoutMS=60000
        )
        return client
    except Exception as e:
        logger.error(f"Error conectando a MongoDB: {e}")
        raise

# Funciones de autenticación
def is_admin(telegram_id):
    """Verifica si un Telegram ID está autorizado"""
    return str(telegram_id) in [str(x) for x in ADMIN_IDS]

def login_required(f):
    """Decorador para requerir login"""
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Rutas
@app.route('/')
def index():
    """Página principal - redirige a login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        telegram_id = request.form.get('telegram_id')
        if telegram_id and is_admin(telegram_id):
            session['admin_id'] = telegram_id
            logger.info(f"Acceso al panel por admin {telegram_id}")
            return redirect(url_for('dashboard'))
        else:
            flash('ID de Telegram no autorizado', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('admin_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        # Obtener estadísticas
        stats = asyncio.run(get_dashboard_stats())
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        flash('Error al cargar el dashboard', 'error')
        return render_template('dashboard.html', stats={})

@app.route('/users')
@login_required
def users():
    """Página de usuarios"""
    try:
        users = asyncio.run(get_users_list())
        return render_template('users.html', users=users)
    except Exception as e:
        logger.error(f"Error en users: {e}")
        flash('Error al cargar usuarios', 'error')
        return render_template('users.html', users=[])

@app.route('/transactions')
@login_required
def transactions():
    """Página de transacciones"""
    try:
        transactions = asyncio.run(get_transactions_list())
        return render_template('transactions.html', transactions=transactions)
    except Exception as e:
        logger.error(f"Error en transactions: {e}")
        flash('Error al cargar transacciones', 'error')
        return render_template('transactions.html', transactions={})

@app.route('/settings')
@login_required
def settings():
    """Página de configuración"""
    try:
        config = asyncio.run(get_system_config())
        return render_template('settings.html', config=config)
    except Exception as e:
        logger.error(f"Error en settings: {e}")
        flash('Error al cargar configuración', 'error')
        return render_template('settings.html', config={})

# API Routes
@app.route('/api/stats')
@login_required
def api_stats():
    """API para estadísticas"""
    try:
        stats = asyncio.run(get_dashboard_stats())
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error en API stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit-user', methods=['POST'])
@login_required
def api_edit_user():
    """API para editar usuario"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        field = data.get('field')
        value = data.get('value')
        
        if not all([user_id, field, value]):
            return jsonify({'error': 'Datos incompletos'}), 400
        
        success = asyncio.run(edit_user_field(user_id, field, value))
        
        if success:
            logger.info(f"Admin {session['admin_id']} editó usuario {user_id}: {field}={value}")
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al editar usuario'}), 500
            
    except Exception as e:
        logger.error(f"Error en API edit user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/approve-deposit', methods=['POST'])
@login_required
def api_approve_deposit():
    """API para aprobar depósitos"""
    try:
        data = request.get_json()
        deposit_id = data.get('deposit_id')
        
        if not deposit_id:
            return jsonify({"success": False, "error": "ID de depósito requerido"})
        
        # Ejecutar función asíncrona
        result = asyncio.run(approve_deposit(deposit_id))
        
        if result["success"]:
            return jsonify({"success": True, "message": "Depósito aprobado correctamente"})
        else:
            return jsonify({"success": False, "error": result["error"]})
            
    except Exception as e:
        logger.error(f"Error en api_approve_deposit: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"})

@app.route('/api/reject-deposit', methods=['POST'])
@login_required
def api_reject_deposit():
    """API para rechazar depósitos"""
    try:
        data = request.get_json()
        deposit_id = data.get('deposit_id')
        reason = data.get('reason', 'Rechazado por administrador')
        
        if not deposit_id:
            return jsonify({"success": False, "error": "ID de depósito requerido"})
        
        result = asyncio.run(reject_deposit(deposit_id, reason))
        
        if result["success"]:
            return jsonify({"success": True, "message": "Depósito rechazado correctamente"})
        else:
            return jsonify({"success": False, "error": result["error"]})
            
    except Exception as e:
        logger.error(f"Error en api_reject_deposit: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"})

@app.route('/api/approve-withdrawal', methods=['POST'])
@login_required
def api_approve_withdrawal():
    """API para aprobar retiros"""
    try:
        data = request.get_json()
        withdrawal_id = data.get('withdrawal_id')
        
        if not withdrawal_id:
            return jsonify({"success": False, "error": "ID de retiro requerido"})
        
        result = asyncio.run(approve_withdrawal(withdrawal_id))
        
        if result["success"]:
            return jsonify({"success": True, "message": "Retiro aprobado correctamente"})
        else:
            return jsonify({"success": False, "error": result["error"]})
            
    except Exception as e:
        logger.error(f"Error en api_approve_withdrawal: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"})

@app.route('/api/reject-withdrawal', methods=['POST'])
@login_required
def api_reject_withdrawal():
    """API para rechazar retiros"""
    try:
        data = request.get_json()
        withdrawal_id = data.get('withdrawal_id')
        reason = data.get('reason', 'Rechazado por administrador')
        
        if not withdrawal_id:
            return jsonify({"success": False, "error": "ID de retiro requerido"})
        
        result = asyncio.run(reject_withdrawal(withdrawal_id, reason))
        
        if result["success"]:
            return jsonify({"success": True, "message": "Retiro rechazado correctamente"})
        else:
            return jsonify({"success": False, "error": result["error"]})
            
    except Exception as e:
        logger.error(f"Error en api_reject_withdrawal: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"})

@app.route('/api/user-inventory/<int:user_id>')
@login_required
def api_user_inventory(user_id):
    """API para obtener inventario de un usuario"""
    try:
        inventory = asyncio.run(get_user_inventory(user_id))
        return jsonify(inventory)
    except Exception as e:
        logger.error(f"Error obteniendo inventario de usuario {user_id}: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/api/backup-database', methods=['POST'])
@login_required
def api_backup_database():
    """API para hacer backup de la base de datos"""
    try:
        result = asyncio.run(backup_database())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error en backup de base de datos: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"})

@app.route('/api/clear-logs', methods=['POST'])
@login_required
def api_clear_logs():
    """API para limpiar logs antiguos"""
    try:
        result = asyncio.run(clear_old_logs())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error limpiando logs: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"})

@app.route('/api/update-system-config', methods=['POST'])
@login_required
def api_update_system_config():
    """API para actualizar configuración del sistema"""
    try:
        data = request.get_json()
        result = asyncio.run(update_system_config(data))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"})

async def approve_deposit(deposit_id):
    """Aprueba un depósito y acredita el balance al usuario"""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        
        # Buscar el depósito
        deposit = await db.creditos.find_one({"_id": ObjectId(deposit_id)})
        if not deposit:
            return {"success": False, "error": "Depósito no encontrado"}
        
        if deposit.get("estado") != "pendiente":
            return {"success": False, "error": "Depósito ya procesado"}
        
        user_id = deposit["user_id"]
        cantidad = deposit.get("cantidad_real", deposit.get("cantidad", 0))
        
        # Acreditar balance al usuario
        from utils.database import agregar_balance_usuario, notificar_credito_agregado
        success = await agregar_balance_usuario(user_id, cantidad)
        
        if not success:
            return {"success": False, "error": "Error al acreditar balance"}
        
        # Actualizar estado del depósito
        await db.creditos.update_one(
            {"_id": ObjectId(deposit_id)},
            {
                "$set": {
                    "estado": "completado",
                    "fecha_procesamiento": datetime.datetime.now(),
                    "procesado_por": session.get('admin_id')
                }
            }
        )
        
        # Notificar al usuario
        try:
            from modules.bot import bot
            await notificar_credito_agregado(bot, user_id, cantidad, "Depósito aprobado")
        except Exception as e:
            logger.warning(f"No se pudo notificar al usuario {user_id}: {e}")
        
        # Log de la acción
        from utils.database import log_action
        await log_action(
            actor_id=session.get('admin_id'),
            action="deposito_aprobado",
            target_id=user_id,
            details={
                "deposit_id": deposit_id,
                "cantidad": cantidad
            }
        )
        
        return {"success": True, "message": f"Depósito aprobado: {cantidad} TON"}
        
    except Exception as e:
        logger.error(f"Error aprobando depósito {deposit_id}: {e}")
        return {"success": False, "error": "Error interno"}

async def reject_deposit(deposit_id, reason):
    """Rechaza un depósito"""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        
        # Buscar el depósito
        deposit = await db.creditos.find_one({"_id": ObjectId(deposit_id)})
        if not deposit:
            return {"success": False, "error": "Depósito no encontrado"}
        
        if deposit.get("estado") != "pendiente":
            return {"success": False, "error": "Depósito ya procesado"}
        
        # Actualizar estado del depósito
        await db.creditos.update_one(
            {"_id": ObjectId(deposit_id)},
            {
                "$set": {
                    "estado": "rechazado",
                    "fecha_procesamiento": datetime.datetime.now(),
                    "procesado_por": session.get('admin_id'),
                    "motivo_rechazo": reason
                }
            }
        )
        
        # Log de la acción
        from utils.database import log_action
        await log_action(
            actor_id=session.get('admin_id'),
            action="deposito_rechazado",
            target_id=deposit["user_id"],
            details={
                "deposit_id": deposit_id,
                "motivo": reason
            }
        )
        
        return {"success": True, "message": "Depósito rechazado"}
        
    except Exception as e:
        logger.error(f"Error rechazando depósito {deposit_id}: {e}")
        return {"success": False, "error": "Error interno"}

async def approve_withdrawal(withdrawal_id):
    """Aprueba un retiro"""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        
        # Buscar el retiro
        withdrawal = await db.creditos.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {"success": False, "error": "Retiro no encontrado"}
        
        if withdrawal.get("estado") != "pendiente":
            return {"success": False, "error": "Retiro ya procesado"}
        
        # Actualizar estado del retiro
        await db.creditos.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "estado": "completado",
                    "fecha_procesamiento": datetime.datetime.now(),
                    "procesado_por": session.get('admin_id')
                }
            }
        )
        
        # Log de la acción
        from utils.database import log_action
        await log_action(
            actor_id=session.get('admin_id'),
            action="retiro_aprobado",
            target_id=withdrawal["user_id"],
            details={
                "withdrawal_id": withdrawal_id,
                "cantidad": withdrawal.get("cantidad_solicitada", 0)
            }
        )
        
        return {"success": True, "message": "Retiro aprobado"}
        
    except Exception as e:
        logger.error(f"Error aprobando retiro {withdrawal_id}: {e}")
        return {"success": False, "error": "Error interno"}

async def reject_withdrawal(withdrawal_id, reason):
    """Rechaza un retiro y devuelve el balance al usuario"""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        
        # Buscar el retiro
        withdrawal = await db.creditos.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {"success": False, "error": "Retiro no encontrado"}
        
        if withdrawal.get("estado") != "pendiente":
            return {"success": False, "error": "Retiro ya procesado"}
        
        user_id = withdrawal["user_id"]
        cantidad = withdrawal.get("cantidad_solicitada", 0)
        
        # Devolver balance al usuario
        from utils.database import agregar_balance_usuario
        success = await agregar_balance_usuario(user_id, cantidad)
        
        if not success:
            return {"success": False, "error": "Error al devolver balance"}
        
        # Actualizar estado del retiro
        await db.creditos.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "estado": "rechazado",
                    "fecha_procesamiento": datetime.datetime.now(),
                    "procesado_por": session.get('admin_id'),
                    "motivo_rechazo": reason
                }
            }
        )
        
        # Log de la acción
        from utils.database import log_action
        await log_action(
            actor_id=session.get('admin_id'),
            action="retiro_rechazado",
            target_id=user_id,
            details={
                "withdrawal_id": withdrawal_id,
                "cantidad_devuelta": cantidad,
                "motivo": reason
            }
        )
        
        return {"success": True, "message": "Retiro rechazado y balance devuelto"}
        
    except Exception as e:
        logger.error(f"Error rechazando retiro {withdrawal_id}: {e}")
        return {"success": False, "error": "Error interno"}

async def get_user_inventory(user_id):
    """Obtiene el inventario completo de un usuario"""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        
        # Obtener usuario
        usuario = await db.usuarios.find_one({"user_id": user_id})
        if not usuario:
            return {"error": "Usuario no encontrado"}
        
        inventario = usuario.get("inventario", {})
        
        # Formatear inventario
        from modules.constants import CRIATURAS_CONFIG, NFTS_CONFIG, obtener_emoji_item, obtener_nombre_item
        
        items_formateados = []
        
        # Procesar criaturas
        for item_key, cantidad in inventario.items():
            if cantidad > 0:
                emoji = obtener_emoji_item(item_key)
                nombre = obtener_nombre_item(item_key)
                
                # Determinar tipo
                if item_key in CRIATURAS_CONFIG:
                    tipo = "Criatura"
                    categoria = CRIATURAS_CONFIG[item_key]["categoria"]
                elif any(nft_config["nombre"] == item_key or item_key == f"{nft_key}-nft" 
                        for nft_key, nft_config in NFTS_CONFIG.items()):
                    tipo = "NFT"
                    # Buscar categoría del NFT
                    for nft_key, nft_config in NFTS_CONFIG.items():
                        if nft_config["nombre"] == item_key or item_key == f"{nft_key}-nft":
                            categoria = nft_config["rareza"]
                            break
                else:
                    tipo = "Otro"
                    categoria = "Desconocida"
                
                items_formateados.append({
                    "item": item_key,
                    "nombre": nombre,
                    "emoji": emoji,
                    "cantidad": cantidad,
                    "tipo": tipo,
                    "categoria": categoria
                })
        
        # Ordenar por tipo y nombre
        items_formateados.sort(key=lambda x: (x["tipo"], x["nombre"]))
        
        return {
            "user_id": user_id,
            "username": usuario.get("username", "Sin username"),
            "first_name": usuario.get("first_name", "Sin nombre"),
            "balance": usuario.get("balance", 0),
            "inventory": items_formateados,
            "total_items": len(items_formateados)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo inventario de usuario {user_id}: {e}")
        return {"error": "Error interno"}

async def backup_database():
    """Realiza backup de la base de datos"""
    try:
        import shutil
        import os
        from datetime import datetime
        
        # Crear directorio de backups si no existe
        backup_dir = "backup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Nombre del archivo de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_file)
        
        client = get_mongo_client()
        db = client[DB_NAME]
        
        # Obtener todas las colecciones
        collections = await db.list_collection_names()
        backup_data = {}
        
        for collection_name in collections:
            collection = db[collection_name]
            documents = await collection.find({}).to_list(None)
            backup_data[collection_name] = documents
        
        # Guardar backup
        import json
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, default=str, indent=2, ensure_ascii=False)
        
        # Log de la acción
        from utils.database import log_action
        await log_action(
            actor_id=session.get('admin_id'),
            action="backup_database",
            details={
                "backup_file": backup_file,
                "collections": len(collections),
                "total_documents": sum(len(docs) for docs in backup_data.values())
            }
        )
        
        return {
            "success": True,
            "message": f"Backup creado exitosamente: {backup_file}",
            "file": backup_file,
            "collections": len(collections),
            "total_documents": sum(len(docs) for docs in backup_data.values())
        }
        
    except Exception as e:
        logger.error(f"Error en backup de base de datos: {e}")
        return {"success": False, "error": str(e)}

async def clear_old_logs():
    """Limpia logs antiguos"""
    try:
        from utils.database import limpiar_logs_antiguos
        
        # Limpiar logs de más de 30 días
        result = await limpiar_logs_antiguos(dias=30)
        
        # Log de la acción
        from utils.database import log_action
        await log_action(
            actor_id=session.get('admin_id'),
            action="clear_logs",
            details={"logs_eliminados": result}
        )
        
        return {
            "success": True,
            "message": f"Se eliminaron {result} logs antiguos",
            "logs_eliminados": result
        }
        
    except Exception as e:
        logger.error(f"Error limpiando logs: {e}")
        return {"success": False, "error": str(e)}

async def update_system_config(config_data):
    """Actualiza la configuración del sistema"""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        
        # Validar datos
        valid_fields = ['min_deposito', 'min_retiro', 'comision_retiro', 'tiempo_procesamiento']
        updates = {}
        
        for field in valid_fields:
            if field in config_data:
                value = config_data[field]
                if field in ['min_deposito', 'min_retiro', 'comision_retiro']:
                    try:
                        value = float(value)
                        if value < 0:
                            return {"success": False, "error": f"{field} debe ser un número positivo"}
                    except ValueError:
                        return {"success": False, "error": f"{field} debe ser un número válido"}
                updates[field] = value
        
        if not updates:
            return {"success": False, "error": "No se proporcionaron datos válidos para actualizar"}
        
        # Actualizar configuración
        await db.configuracion.update_one(
            {"tipo": "sistema"},
            {"$set": updates},
            upsert=True
        )
        
        # Log de la acción
        from utils.database import log_action
        await log_action(
            actor_id=session.get('admin_id'),
            action="update_system_config",
            details={"updates": updates}
        )
        
        return {
            "success": True,
            "message": "Configuración actualizada correctamente",
            "updates": updates
        }
        
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        return {"success": False, "error": str(e)}

# Funciones asíncronas para MongoDB
async def get_dashboard_stats():
    """Obtiene estadísticas del dashboard"""
    client = get_mongo_client()
    db = client[DB_NAME]
    
    try:
        # Estadísticas básicas
        total_users = await db.usuarios.count_documents({})
        total_deposits = await db.depositos.count_documents({})
        total_withdrawals = await db.creditos.count_documents({"tipo": "retiro"})
        
        # Volumen total
        pipeline = [
            {"$match": {"estado": "procesado"}},
            {"$group": {"_id": None, "total": {"$sum": "$cantidad_real"}}}
        ]
        result = await db.depositos.aggregate(pipeline).to_list(1)
        total_volume = result[0]["total"] if result else 0
        
        # Usuarios activos (últimos 7 días)
        week_ago = datetime.now() - timedelta(days=7)
        active_users = await db.usuarios.count_documents({
            "ultima_actividad": {"$gte": week_ago}
        })
        
        return {
            'total_users': total_users,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_volume': total_volume,
            'active_users': active_users,
        }
        
    finally:
        client.close()

async def get_users_list():
    """Obtiene lista de usuarios"""
    client = get_mongo_client()
    db = client[DB_NAME]
    
    try:
        cursor = db.usuarios.find().sort("fecha_registro", -1).limit(100)
        users = await cursor.to_list(length=100)
        return users
    finally:
        client.close()

async def get_transactions_list():
    """Obtiene lista de transacciones"""
    client = get_mongo_client()
    db = client[DB_NAME]
    
    try:
        # Depósitos (buscar en creditos con tipo "deposito")
        deposits = await db.creditos.find({"tipo": "deposito"}).sort("fecha", -1).limit(50).to_list(50)
        
        # Retiros (buscar en creditos con tipo "retiro")
        withdrawals = await db.creditos.find({"tipo": "retiro"}).sort("fecha", -1).limit(50).to_list(50)
        
        return {
            'deposits': deposits,
            'withdrawals': withdrawals
        }
    finally:
        client.close()

async def get_system_config():
    """Obtiene configuración del sistema"""
    return {
        'min_deposit': float(os.getenv('MIN_DEPOSITO', '0.5')),
        'min_withdrawal': float(os.getenv('MIN_RETIRO', '1.1')),
        'commission': float(os.getenv('COMISION_RETIRO', '0.1')),
        'processing_time': os.getenv('TIEMPO_PROCESAMIENTO', '24-48h'),
    }

async def edit_user_field(user_id, field, value):
    """Edita un campo de usuario"""
    client = get_mongo_client()
    db = client[DB_NAME]
    
    try:
        # Convertir balance a float si es necesario
        if field == "balance":
            try:
                value = float(value)
            except ValueError:
                return False
        
        result = await db.usuarios.update_one(
            {"user_id": int(user_id)},
            {"$set": {field: value}}
        )
        return result.modified_count > 0
    finally:
        client.close()

# Funciones de utilidad
def format_balance(balance):
    """Formatea balance para mostrar"""
    try:
        return f"{float(balance):.3f} TON"
    except:
        return "0.000 TON"

def format_date(date):
    """Formatea fecha para mostrar"""
    try:
        return date.strftime("%d/%m/%Y %H:%M")
    except:
        return "N/A"

def get_status_badge(status):
    """Obtiene badge de estado"""
    badges = {
        'pendiente': '<span class="badge bg-warning">Pendiente</span>',
        'procesado': '<span class="badge bg-success">Procesado</span>',
        'cancelado': '<span class="badge bg-danger">Cancelado</span>',
        'rechazado': '<span class="badge bg-danger">Rechazado</span>',
    }
    return badges.get(status, f'<span class="badge bg-secondary">{status}</span>')

# Context processors para templates
@app.context_processor
def utility_processor():
    """Procesador de contexto para funciones de utilidad"""
    return {
        'format_balance': format_balance,
        'format_date': format_date,
        'get_status_badge': get_status_badge
    }

if __name__ == '__main__':
    # Crear directorio de templates si no existe
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=8000, debug=True) 