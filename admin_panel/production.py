import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB para producción
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'mundo_mitico')

# Configuración de administradores
ADMIN_IDS = [int(id.strip()) for id in os.environ.get('ADMIN_IDS', '7828962018').split(',')]

# Configuración de seguridad para producción
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configuración del servidor para producción
FLASK_HOST = '0.0.0.0'
FLASK_PORT = int(os.environ.get('PORT', '5000'))
FLASK_DEBUG = False  # Siempre False en producción

# Configuración adicional para producción
class ProductionConfig:
    SECRET_KEY = ADMIN_SECRET_KEY
    DEBUG = False
    TESTING = False
    # Configuración de sesiones seguras
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',') 