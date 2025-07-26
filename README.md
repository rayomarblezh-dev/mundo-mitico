# Mundo Mítico Bot

Bot de Telegram para el juego Mundo Mítico.

## 🚀 Arquitectura

Bot de Telegram independiente que se conecta a MongoDB Atlas para gestionar el juego Mundo Mítico.

### **Servicio: Bot de Telegram** 🤖
- **Tecnología**: Python + Aiogram
- **Repositorio**: `mundo-mitico` (este)
- **Función**: Bot de Telegram con todos los comandos del juego
- **Despliegue**: Railway

### **Base de Datos** 🗄️
- **MongoDB Atlas**: Base de datos principal del juego
- **Colecciones**: Usuarios, transacciones, inventario, etc.

## 🛠️ Tecnologías

### **Bot de Telegram:**
- **Backend**: Python + Aiogram 3.x
- **Base de Datos**: MongoDB Atlas (Motor)
- **HTTP Client**: httpx para APIs externas
- **Despliegue**: Railway

## 📋 Estructura del Proyecto

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
```

4. **Ejecutar:**
```bash
python main.py
```

## 🌐 Despliegue

### **Bot de Telegram en Railway:**

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

## 🔗 Base de Datos

### **MongoDB Atlas:**
- **Base de datos**: `mundomi`
- **Colecciones principales**:
  - `users` - Usuarios del bot
  - `deposits` - Depósitos (status: pending/completed/cancelled)
  - `withdrawals` - Retiros (status: pending/completed/cancelled)
  - `inventory` - Inventario de usuarios
  - `creatures` - Criaturas del juego
  - `nfts` - NFTs de usuarios

## 🔒 Seguridad

- **Autenticación**: Verificación de usuarios a través de Telegram
- **Validación**: Verificación de datos en todos los comandos
- **Logs**: Registro de todas las acciones importantes

## 🚨 Troubleshooting

### **Error de conexión a MongoDB:**
- Verificar `MONGO_URI` y credenciales
- Comprobar que la IP esté en whitelist de MongoDB Atlas

### **Bot no responde:**
- Verificar `BOT_TOKEN`
- Comprobar logs en Railway
- Verificar que solo haya una instancia ejecutándose

### **Error de módulo httpx:**
- Verificar que `httpx` esté en `requirements.txt`
- Reinstalar dependencias: `pip install -r requirements.txt`

## 📞 Soporte

Para problemas o consultas:
1. Revisar logs en Railway
2. Verificar configuración de variables de entorno
3. Comprobar conexión a MongoDB Atlas

---

**Desarrollado para Mundo Mítico Bot** 🤖 