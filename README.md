# Mundo Mítico Bot

Bot de Telegram para el juego Mundo Mítico con panel de administración web separado.

## 🚀 Arquitectura

El proyecto está dividido en **2 servicios independientes** que comparten la misma base de datos MongoDB:

### **Servicio 1: Bot de Telegram** 🤖
- **Tecnología**: Python + Aiogram
- **Repositorio**: `mundo-mitico` (este)
- **Función**: Bot de Telegram con todos los comandos del juego
- **Despliegue**: Railway

### **Servicio 2: Panel de Administración** 🌐
- **Tecnología**: Flask + Gunicorn
- **Repositorio**: `mundomitico-admin` (separado)
- **Función**: Panel web para administradores
- **Despliegue**: Railway

### **Base de Datos Compartida** 🗄️
- **MongoDB Atlas**: Ambos servicios se conectan a la misma base de datos
- **Sincronización**: Cambios en tiempo real entre bot y panel

## 🛠️ Tecnologías

### **Bot de Telegram:**
- **Backend**: Python + Aiogram 3.x
- **Base de Datos**: MongoDB Atlas (Motor)
- **Despliegue**: Railway

### **Panel de Administración:**
- **Backend**: Flask + Gunicorn
- **Frontend**: HTML + JavaScript + Tailwind CSS
- **Base de Datos**: MongoDB Atlas (Motor)
- **Despliegue**: Railway

## 📋 Estructura del Proyecto (Bot)

```
mundo-mitico/
├── main.py              # Entrada principal del bot
├── config/
│   └── config.py        # Configuración centralizada
├── modules/
│   ├── bot.py           # Configuración del bot
│   ├── commands.py      # Comandos del bot
│   ├── wallet.py        # Funciones de wallet
│   ├── tienda.py        # Sistema de tienda
│   ├── inventario.py    # Sistema de inventario
│   ├── explorar.py      # Sistema de exploración
│   ├── tareas.py        # Sistema de tareas
│   ├── referidos.py     # Sistema de referidos
│   ├── criaturas.py     # Sistema de criaturas
│   ├── nfts.py          # Sistema de NFTs
│   └── recompensas.py   # Sistema de recompensas
├── utils/
│   ├── database.py      # Conexión a MongoDB
│   └── logging_config.py
├── requirements.txt     # Dependencias del bot
└── railway.json        # Configuración de Railway
```

## 🔧 Instalación Local (Bot)

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
ADMIN_PANEL_URL=https://mundomitico-admin.up.railway.app
```

4. **Ejecutar:**
```bash
python main.py
```

## 🌐 Despliegue

### **1. Bot de Telegram en Railway:**

1. **Crear proyecto en Railway:**
   - Ve a [Railway Dashboard](https://railway.app/dashboard)
   - **"New Project"** → **"Deploy from GitHub repo"**
   - Selecciona el repositorio `mundo-mitico`
   - **"Deploy"**

2. **Configurar variables de entorno:**
```env
BOT_TOKEN=7878980636:AAFnvq7emNzPXNqj2eliCE4P7O5bhW4fZX8
MONGO_URI=mongodb+srv://rayomarblezh:tatico.10@telegram.yxpl0n0.mongodb.net/?retryWrites=true&w=majority&appName=Telegram&ssl=true&ssl_cert_reqs=CERT_NONE
DB_NAME=mundomi
ADMIN_IDS=7828962018
ADMIN_PANEL_URL=https://mundomitico-admin.up.railway.app
```

### **2. Panel de Administración en Railway:**

1. **Crear proyecto separado:**
   - Ve a [Railway Dashboard](https://railway.app/dashboard)
   - **"New Project"** → **"Deploy from GitHub repo"**
   - Selecciona el repositorio `mundomitico-admin`
   - **"Deploy"**

2. **Configurar variables de entorno:**
```env
MONGO_URI=mongodb+srv://rayomarblezh:tatico.10@telegram.yxpl0n0.mongodb.net/?retryWrites=true&w=majority&appName=Telegram&ssl=true&ssl_cert_reqs=CERT_NONE
DATABASE_NAME=mundomi
ADMIN_IDS=7828962018
ADMIN_SECRET_KEY=V7rX!p9Lq$3tZ@fM
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

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

## 🔗 Integración entre Servicios

### **Base de Datos Compartida:**
- **MongoDB Atlas**: `mundomi`
- **Colecciones principales**:
  - `users` - Usuarios del bot
  - `deposits` - Depósitos (status: pending/completed/cancelled)
  - `withdrawals` - Retiros (status: pending/completed/cancelled)
  - `admin_actions` - Log de acciones de administradores

### **Sincronización:**
1. **Bot → Panel**: Los depósitos/retiros creados en el bot aparecen inmediatamente en el panel
2. **Panel → Bot**: Los cambios procesados en el panel se reflejan inmediatamente en el bot
3. **Tiempo real**: Ambos servicios leen/escriben en la misma base de datos

### **Comunicación:**
- **Directa**: A través de MongoDB (no hay API entre servicios)
- **Eficiente**: Sin latencia adicional
- **Confiable**: Transacciones atómicas de MongoDB

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

### **Bot no responde:**
- Verificar `BOT_TOKEN`
- Comprobar logs en Railway
- Verificar que solo haya una instancia ejecutándose

### **Panel no sincroniza:**
- Verificar que ambos servicios usen la misma `MONGO_URI`
- Comprobar que usen la misma `DATABASE_NAME`
- Revisar logs de ambos servicios

## 📞 Soporte

Para problemas o consultas:
1. Revisar logs en Railway (ambos servicios)
2. Verificar configuración de variables de entorno
3. Comprobar conexión a MongoDB Atlas
4. Verificar sincronización entre servicios

## 🔄 Flujo de Trabajo

1. **Usuario hace depósito** → Bot lo registra en MongoDB
2. **Admin ve depósito** → Panel lee desde MongoDB
3. **Admin procesa depósito** → Panel actualiza MongoDB
4. **Usuario ve balance actualizado** → Bot lee desde MongoDB

---

**Desarrollado para Mundo Mítico Bot** 🤖 