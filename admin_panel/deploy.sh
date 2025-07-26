#!/bin/bash

# Script de despliegue para el Panel de Administración
# Uso: ./deploy.sh

echo "🚀 Iniciando despliegue del Panel de Administración..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Verificar variables de entorno
if [ -z "$MONGO_URI" ]; then
    echo "⚠️  MONGO_URI no está configurado"
fi

if [ -z "$ADMIN_IDS" ]; then
    echo "⚠️  ADMIN_IDS no está configurado"
fi

if [ -z "$ADMIN_SECRET_KEY" ]; then
    echo "⚠️  ADMIN_SECRET_KEY no está configurado"
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << EOF
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=mundo_mitico
ADMIN_IDS=7828962018
ADMIN_SECRET_KEY=your-secret-key-change-this-in-production
FLASK_DEBUG=False
EOF
    echo "⚠️  Archivo .env creado con valores por defecto. ¡Configúralo antes de usar en producción!"
fi

# Verificar conexión a MongoDB
echo "🔍 Verificando conexión a MongoDB..."
python3 -c "
import motor.motor_asyncio
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URI'))
        await client.admin.command('ping')
        print('✅ Conexión a MongoDB exitosa')
        return True
    except Exception as e:
        print(f'❌ Error conectando a MongoDB: {e}')
        return False

asyncio.run(test_connection())
"

# Iniciar aplicación
echo "🚀 Iniciando aplicación..."
if [ "$1" = "production" ]; then
    echo "🏭 Modo producción con Gunicorn..."
    gunicorn --bind 0.0.0.0:5000 --workers 3 wsgi:app
else
    echo "🔧 Modo desarrollo..."
    python3 app.py
fi 