from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import datetime
from functools import wraps
import motor.motor_asyncio
import asyncio
from bson import ObjectId
import json

# Configuración
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'mundo_mitico')
ADMIN_IDS = [int(id.strip()) for id in os.environ.get('ADMIN_IDS', '7828962018').split(',')]
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'your-secret-key-change-this-in-production')
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', '5000'))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

app = Flask(__name__)
app.secret_key = ADMIN_SECRET_KEY
CORS(app)

# Configuración de MongoDB
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
except Exception as e:
    print(f"Error conectando a MongoDB: {e}")
    db = None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Endpoint de health check para monitoreo"""
    try:
        # Verificar conexión a MongoDB
        if db:
            # Intentar una operación simple
            asyncio.run(db.admin.command('ping'))
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    admin_id = int(data.get('admin_id', 0))
    
    if admin_id in ADMIN_IDS:
        session['admin_id'] = admin_id
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'ID de administrador no válido'})

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
@admin_required
def get_stats():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        stats = loop.run_until_complete(get_statistics())
        return jsonify(stats)
    finally:
        loop.close()

@app.route('/api/deposits')
@admin_required
def get_deposits():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        deposits = loop.run_until_complete(get_pending_deposits())
        return jsonify(deposits)
    finally:
        loop.close()

@app.route('/api/withdrawals')
@admin_required
def get_withdrawals():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        withdrawals = loop.run_until_complete(get_pending_withdrawals())
        return jsonify(withdrawals)
    finally:
        loop.close()

@app.route('/api/process-deposit', methods=['POST'])
@admin_required
def process_deposit():
    data = request.get_json()
    deposit_id = data.get('deposit_id')
    amount = float(data.get('amount', 0))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(process_deposit_async(deposit_id, amount, session['admin_id']))
        return jsonify(result)
    finally:
        loop.close()

@app.route('/api/process-withdrawal', methods=['POST'])
@admin_required
def process_withdrawal():
    data = request.get_json()
    withdrawal_id = data.get('withdrawal_id')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(process_withdrawal_async(withdrawal_id, session['admin_id']))
        return jsonify(result)
    finally:
        loop.close()

@app.route('/api/cancel-deposit', methods=['POST'])
@admin_required
def cancel_deposit():
    data = request.get_json()
    deposit_id = data.get('deposit_id')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(cancel_deposit_async(deposit_id, session['admin_id']))
        return jsonify(result)
    finally:
        loop.close()

@app.route('/api/cancel-withdrawal', methods=['POST'])
@admin_required
def cancel_withdrawal():
    data = request.get_json()
    withdrawal_id = data.get('withdrawal_id')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(cancel_withdrawal_async(withdrawal_id, session['admin_id']))
        return jsonify(result)
    finally:
        loop.close()

# Funciones asíncronas para interactuar con MongoDB
async def get_statistics():
    if not db:
        return {
            'total_users': 0,
            'total_deposits': 0,
            'total_withdrawals': 0,
            'total_volume': 0,
            'active_users': 0
        }
    
    try:
        total_users = await db.usuarios.count_documents({})
        total_deposits = await db.depositos.count_documents({})
        total_withdrawals = await db.creditos.count_documents({"tipo": "retiro"})
        
        # Calcular volumen total
        pipeline = [
            {"$match": {"estado": "procesado"}},
            {"$group": {"_id": None, "total": {"$sum": "$cantidad_real"}}}
        ]
        volume_result = await db.depositos.aggregate(pipeline).to_list(1)
        total_volume = volume_result[0]['total'] if volume_result else 0
        
        # Usuarios activos en los últimos 7 días
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        active_users = await db.usuarios.count_documents({
            "ultima_actividad": {"$gte": seven_days_ago}
        })
        
        return {
            'total_users': total_users,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_volume': round(total_volume, 2),
            'active_users': active_users
        }
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            'total_users': 0,
            'total_deposits': 0,
            'total_withdrawals': 0,
            'total_volume': 0,
            'active_users': 0
        }

async def get_pending_deposits():
    if not db:
        return []
    
    try:
        deposits = await db.depositos.find({"estado": "pendiente"}).sort("fecha", -1).to_list(50)
        return [{
            'id': str(dep['_id']),
            'user_id': dep['user_id'],
            'amount': dep.get('cantidad', 0),
            'network': dep.get('network_name', 'TON'),
            'hash': dep.get('hash', ''),
            'date': dep['fecha'].isoformat() if 'fecha' in dep else '',
            'address': dep.get('address', '')
        } for dep in deposits]
    except Exception as e:
        print(f"Error getting deposits: {e}")
        return []

async def get_pending_withdrawals():
    if not db:
        return []
    
    try:
        withdrawals = await db.creditos.find({
            "tipo": "retiro",
            "estado": "pendiente"
        }).sort("fecha", -1).to_list(50)
        
        return [{
            'id': str(w['_id']),
            'user_id': w['user_id'],
            'amount': w.get('cantidad', 0),
            'wallet': w.get('wallet', ''),
            'date': w['fecha'].isoformat() if 'fecha' in w else ''
        } for w in withdrawals]
    except Exception as e:
        print(f"Error getting withdrawals: {e}")
        return []

async def process_deposit_async(deposit_id, amount, admin_id):
    if not db:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Buscar el depósito
        deposit = await db.depositos.find_one({"_id": ObjectId(deposit_id)})
        if not deposit:
            return {'success': False, 'message': 'Depósito no encontrado'}
        
        if deposit.get("estado") != "pendiente":
            return {'success': False, 'message': 'Depósito ya procesado'}
        
        user_id = deposit["user_id"]
        
        # Actualizar depósito como procesado
        await db.depositos.update_one(
            {"_id": ObjectId(deposit_id)},
            {
                "$set": {
                    "estado": "procesado",
                    "cantidad_real": amount,
                    "admin_id": admin_id,
                    "fecha_procesamiento": datetime.datetime.now()
                }
            }
        )
        
        # Agregar balance al usuario
        await db.usuarios.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}}
        )
        
        # Log de la acción
        await db.logs.insert_one({
            "admin_id": admin_id,
            "action": "deposito_procesado",
            "target_id": user_id,
            "extra": {
                "deposito_id": deposit_id,
                "cantidad_real": amount
            },
            "fecha": datetime.datetime.now()
        })
        
        return {'success': True, 'message': 'Depósito procesado exitosamente'}
    except Exception as e:
        print(f"Error processing deposit: {e}")
        return {'success': False, 'message': 'Error interno del servidor'}

async def process_withdrawal_async(withdrawal_id, admin_id):
    if not db:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Buscar el retiro
        withdrawal = await db.creditos.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        if withdrawal.get("estado") != "pendiente":
            return {'success': False, 'message': 'Retiro ya procesado'}
        
        user_id = withdrawal["user_id"]
        
        # Actualizar retiro como procesado
        await db.creditos.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "estado": "procesado",
                    "admin_id": admin_id,
                    "fecha_procesamiento": datetime.datetime.now()
                }
            }
        )
        
        # Log de la acción
        await db.logs.insert_one({
            "admin_id": admin_id,
            "action": "retiro_procesado",
            "target_id": user_id,
            "extra": {
                "retiro_id": withdrawal_id,
                "cantidad": withdrawal.get("cantidad", 0)
            },
            "fecha": datetime.datetime.now()
        })
        
        return {'success': True, 'message': 'Retiro procesado exitosamente'}
    except Exception as e:
        print(f"Error processing withdrawal: {e}")
        return {'success': False, 'message': 'Error interno del servidor'}

async def cancel_deposit_async(deposit_id, admin_id):
    if not db:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar depósito como cancelado
        await db.depositos.update_one(
            {"_id": ObjectId(deposit_id)},
            {
                "$set": {
                    "estado": "cancelado",
                    "admin_id": admin_id,
                    "fecha_cancelacion": datetime.datetime.now()
                }
            }
        )
        
        # Log de la acción
        await db.logs.insert_one({
            "admin_id": admin_id,
            "action": "deposito_cancelado",
            "extra": {"deposito_id": deposit_id},
            "fecha": datetime.datetime.now()
        })
        
        return {'success': True, 'message': 'Depósito cancelado exitosamente'}
    except Exception as e:
        print(f"Error canceling deposit: {e}")
        return {'success': False, 'message': 'Error interno del servidor'}

async def cancel_withdrawal_async(withdrawal_id, admin_id):
    if not db:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Buscar el retiro
        withdrawal = await db.creditos.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        user_id = withdrawal["user_id"]
        amount = withdrawal.get("cantidad", 0)
        
        # Devolver el balance al usuario
        await db.usuarios.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}}
        )
        
        # Actualizar retiro como cancelado
        await db.creditos.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "estado": "cancelado",
                    "admin_id": admin_id,
                    "fecha_cancelacion": datetime.datetime.now()
                }
            }
        )
        
        # Log de la acción
        await db.logs.insert_one({
            "admin_id": admin_id,
            "action": "retiro_cancelado",
            "target_id": user_id,
            "extra": {
                "retiro_id": withdrawal_id,
                "cantidad_devuelta": amount
            },
            "fecha": datetime.datetime.now()
        })
        
        return {'success': True, 'message': 'Retiro cancelado y fondos devueltos'}
    except Exception as e:
        print(f"Error canceling withdrawal: {e}")
        return {'success': False, 'message': 'Error interno del servidor'}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', FLASK_PORT))
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=port) 