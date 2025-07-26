import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB (usar la misma que el bot)
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'mundo_mitico')

# Configuración de administradores
ADMIN_IDS = [int(id.strip()) for id in os.environ.get('ADMIN_IDS', '7828962018').split(',')]

# Configuración de seguridad
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configuración del servidor
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', '5000'))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' 