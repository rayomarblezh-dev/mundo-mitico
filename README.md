# Mundo Mítico Bot

Bot de Telegram para el juego Mundo Mítico con panel de administración web integrado.

## 🚀 Características

- **Bot de Telegram**: Completamente funcional con Aiogram
- **Panel de Administración**: Web integrado con Flask
- **API REST**: FastAPI para endpoints del bot
- **Base de Datos**: MongoDB Atlas
- **Despliegue**: Railway con integración completa

## 🛠️ Tecnologías

- **Backend**: FastAPI + Flask (integrados)
- **Bot**: Aiogram 3.x
- **Base de Datos**: MongoDB Atlas
- **Frontend**: HTML + JavaScript + Tailwind CSS
- **Despliegue**: Railway

## 📋 Estructura del Proyecto

```
mundo-mitico/
├── main.py              # FastAPI + Flask integrados
├── config/
│   └── config.py        # Configuración centralizada
├── modules/
│   ├── bot.py           # Configuración del bot
│   ├── commands.py      # Comandos del bot
│   ├── wallet.py        # Funciones de wallet
│   └── ...              # Otros módulos
├── templates/
│   ├── login.html       # Panel de login
│   └── dashboard.html   # Panel principal
├── utils/
│   ├── database.py      # Conexión a MongoDB
│   └── logging_config.py
├── requirements.txt     # Dependencias
└── railway.json        # Configuración de Railway
```

## 🔧 Instalación Local

1. **Clonar el repositorio:**
```bash
git clone <repo-url>
cd mundo-mitico
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
# Crear archivo .env
BOT_TOKEN=tu_token_aqui
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=mundomi
ADMIN_IDS=7828962018
ADMIN_SECRET_KEY=tu_secret_key
API_HOST=0.0.0.0
API_PORT=3000
API_WORKERS=1
ADMIN_PANEL_URL=/admin
```

4. **Ejecutar:**
```bash
python main.py
```

## 🌐 Despliegue en Railway

### **1. Crear Proyecto en Railway:**
1. Ve a [Railway Dashboard](https://railway.app/dashboard)
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Selecciona tu repositorio `mundo-mitico`
4. **"Deploy"**

### **2. Configurar Variables de Entorno:**
En Railway, agrega estas variables:

```env
BOT_TOKEN=7878980636:AAFnvq7emNzPXNqj2eliCE4P7O5bhW4fZX8
MONGO_URI=mongodb+srv://rayomarblezh:tatico.10@telegram.yxpl0n0.mongodb.net/?retryWrites=true&w=majority&appName=Telegram&ssl=true&ssl_cert_reqs=CERT_NONE
DB_NAME=mundomi
ADMIN_IDS=7828962018
ADMIN_SECRET_KEY=V7rX!p9Lq$3tZ@fM
API_HOST=0.0.0.0
API_PORT=3000
API_WORKERS=1
ADMIN_PANEL_URL=/admin
```

### **3. URLs del Servicio:**
Una vez desplegado, tendrás acceso a:

- **Bot API**: `https://tu-bot-url.up.railway.app`
- **Panel de Admin**: `https://tu-bot-url.up.railway.app/admin`
- **Documentación API**: `https://tu-bot-url.up.railway.app/docs`
- **Health Check**: `https://tu-bot-url.up.railway.app/health`

## 📊 Funcionalidades

### **Bot de Telegram:**
- `/start` - Iniciar bot
- `/wallet` - Gestionar wallet
- `/tienda` - Tienda del juego
- `/inventario` - Ver inventario
- `/explorar` - Explorar mundo
- `/tareas` - Sistema de tareas
- `/referidos` - Sistema de referidos
- `/admin` - Panel de administración (solo admins)

### **Panel de Administración:**
- **Login**: Autenticación con ID de Telegram
- **Dashboard**: Estadísticas en tiempo real
- **Depósitos**: Procesar/cancelar depósitos pendientes
- **Retiros**: Procesar/cancelar retiros pendientes
- **Logs**: Registro de acciones de administradores

### **API Endpoints:**
- `GET /` - Información del bot
- `GET /health` - Health check
- `GET /status` - Estado del bot
- `GET /stats` - Estadísticas del sistema
- `GET /info` - Información general
- `POST /restart` - Reiniciar bot
- `GET /admin-panel-url` - URL del panel

## 🔗 Integración FastAPI + Flask

### **Cómo funciona:**
1. **FastAPI**: Maneja la API del bot y endpoints principales
2. **Flask**: Maneja el panel de administración web
3. **WSGIMiddleware**: Integra Flask dentro de FastAPI
4. **Un solo puerto**: Todo funciona en el puerto de Railway

### **Rutas:**
- **FastAPI**: `/`, `/health`, `/status`, `/docs`, etc.
- **Flask**: `/admin/*` (montado en FastAPI)

## 🎨 Diseño del Panel

- **Tema**: Oscuro con elementos transparentes
- **Colores**: Monocromático (blanco, negro, gris)
- **Responsive**: Adaptable a móviles y desktop
- **Grid background**: Fondo cuadricular sutil
- **Sin iconos**: Diseño minimalista

## 🔒 Seguridad

- **Autenticación**: Solo IDs de administrador autorizados
- **Sesiones**: Cookies httponly para sesiones
- **CORS**: Configurado para permitir conexiones seguras
- **Validación**: Verificación de datos en todos los endpoints

## 📝 Logs

El sistema registra todas las acciones en MongoDB:

```json
{
  "admin_id": 7828962018,
  "action": "process_deposit",
  "deposit_id": ObjectId("..."),
  "amount": 100.0,
  "user_id": 123456789,
  "timestamp": "2025-07-26T15:30:00Z"
}
```

## 🚨 Troubleshooting

### **Error de conexión a MongoDB:**
- Verificar `MONGO_URI` y credenciales
- Comprobar que la IP esté en whitelist de MongoDB Atlas

### **Error de autenticación:**
- Verificar que el `ADMIN_IDS` contenga el ID correcto
- Limpiar cookies del navegador

### **Error de puerto:**
- Railway asigna automáticamente el puerto
- Verificar que no haya conflictos

### **Bot no responde:**
- Verificar `BOT_TOKEN`
- Comprobar logs en Railway
- Verificar que solo haya una instancia ejecutándose

## 📞 Soporte

Para problemas o consultas:
1. Revisar logs en Railway
2. Verificar configuración de variables de entorno
3. Comprobar conexión a MongoDB Atlas
4. Verificar estado del bot en `/health`

---

**Desarrollado para Mundo Mítico Bot** 🤖 