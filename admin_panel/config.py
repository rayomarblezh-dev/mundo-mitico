import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'mundo_mitico')

# Configuración de administradores
ADMIN_IDS = [int(id.strip()) for id in os.environ.get('ADMIN_IDS', '7828962018').split(',')]

# Configuración de seguridad
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY')

# Configuración del servidor
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
# En Railway, usar la variable PORT que asigna automáticamente
FLASK_PORT = int(os.environ.get('PORT', os.environ.get('FLASK_PORT', '5001')))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# URL del panel (para despliegue)
PANEL_URL = os.environ.get('PANEL_URL', 'http://localhost:5001')

# Si está desplegado en Railway (usar la URL pública automática)
if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
    PANEL_URL = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}"

# Si está desplegado en Railway (URL estática)
elif os.environ.get('RAILWAY_STATIC_URL'):
    PANEL_URL = os.environ.get('RAILWAY_STATIC_URL')

# Si está desplegado en Render
elif os.environ.get('RENDER_EXTERNAL_URL'):
    PANEL_URL = os.environ.get('RENDER_EXTERNAL_URL')

# Si está desplegado en Heroku
elif os.environ.get('HEROKU_APP_NAME'):
    PANEL_URL = f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com"

# Si hay un dominio personalizado
elif os.environ.get('DOMAIN'):
    PANEL_URL = f"https://{os.environ.get('DOMAIN')}" 