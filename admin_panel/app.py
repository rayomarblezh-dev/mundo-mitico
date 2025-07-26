from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import datetime
from functools import wraps
import motor.motor_asyncio
import asyncio
from bson import ObjectId

# Configuración
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://rayomarblezh:tatico.10@telegram.yxpl0n0.mongodb.net/?retryWrites=true&w=majority&appName=Telegram&ssl=true&ssl_cert_reqs=CERT_NONE')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'mundomi')
ADMIN_IDS = [int(id.strip()) for id in os.environ.get('ADMIN_IDS', '7828962018').split(',')]
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'V7rX!p9Lq$3tZ@fM')
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '5000'))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

app = Flask(__name__)
app.secret_key = ADMIN_SECRET_KEY
CORS(app)

# Configuración de MongoDB
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    print(f"✅ Conectado a MongoDB: {DATABASE_NAME}")
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    db = None

# Simulación de sesiones
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

@app.route('/')
def index():
    admin_id = get_admin_id(request)
    if admin_id and admin_id in ADMIN_IDS:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Endpoint de health check para monitoreo"""
    try:
        # Verificar conexión a MongoDB
        if db is not None:
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

@app.route('/logout')
def logout():
    session_id = request.cookies.get("admin_session")
    if session_id in admin_sessions:
        del admin_sessions[session_id]
    
    response = redirect(url_for('login'))
    response.delete_cookie("admin_session")
    return response

@app.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
@admin_required
def get_stats():
    """Obtener estadísticas del sistema"""
    try:
        stats = asyncio.run(get_statistics())
        return jsonify(stats)
    except Exception as e:
        import traceback
        print('Error en /api/stats:', traceback.format_exc())
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/deposits')
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

@app.route('/api/withdrawals')
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

@app.route('/api/process-deposit', methods=['POST'])
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

@app.route('/api/process-withdrawal', methods=['POST'])
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

@app.route('/api/cancel-deposit', methods=['POST'])
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

@app.route('/api/cancel-withdrawal', methods=['POST'])
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

# Funciones asíncronas para interactuar con MongoDB
async def get_statistics():
    if db is None:
        return {
            'total_users': 0,
            'total_deposits': 0,
            'total_withdrawals': 0,
            'total_volume': 0,
            'active_users': 0
        }
    
    try:
        # Obtener estadísticas de usuarios
        total_users = await db.users.count_documents({})
        
        # Obtener estadísticas de depósitos
        total_deposits = await db.deposits.count_documents({})
        deposits_volume = await db.deposits.aggregate([
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        total_volume = deposits_volume[0]['total'] if deposits_volume else 0
        
        # Obtener estadísticas de retiros
        total_withdrawals = await db.withdrawals.count_documents({})
        
        # Usuarios activos en los últimos 7 días
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        active_users = await db.users.count_documents({
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
    if db is None:
        return []
    
    try:
        deposits = await db.deposits.find({"status": "pending"}).to_list(100)
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
    if db is None:
        return []
    
    try:
        withdrawals = await db.withdrawals.find({"status": "pending"}).to_list(100)
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
    if db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el depósito
        result = await db.deposits.update_one(
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
        deposit = await db.deposits.find_one({"_id": ObjectId(deposit_id)})
        if not deposit:
            return {'success': False, 'message': 'Depósito no encontrado'}
        
        user_id = deposit.get('user_id')
        
        # Actualizar balance del usuario
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}},
            upsert=True
        )
        
        # Registrar la acción del admin
        await db.admin_actions.insert_one({
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
    if db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el retiro
        result = await db.withdrawals.update_one(
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
        withdrawal = await db.withdrawals.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        user_id = withdrawal.get('user_id')
        amount = withdrawal.get('amount', 0)
        
        # Registrar la acción del admin
        await db.admin_actions.insert_one({
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
    if db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el depósito
        result = await db.deposits.update_one(
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
        await db.admin_actions.insert_one({
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
    if db is None:
        return {'success': False, 'message': 'Error de conexión a la base de datos'}
    
    try:
        # Actualizar el retiro
        result = await db.withdrawals.update_one(
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
        withdrawal = await db.withdrawals.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            return {'success': False, 'message': 'Retiro no encontrado'}
        
        user_id = withdrawal.get('user_id')
        amount = withdrawal.get('amount', 0)
        
        # Devolver el balance al usuario
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}},
            upsert=True
        )
        
        # Registrar la acción del admin
        await db.admin_actions.insert_one({
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

if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    ) 