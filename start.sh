#!/bin/bash

# Obtener el puerto de la variable de entorno o usar 443 por defecto
PORT=${PORT:-443}

echo "🚀 Iniciando Mundo Mítico Bot en puerto $PORT"

# Ejecutar la aplicación FastAPI
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 