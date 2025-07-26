# Panel de Administración - Mundo Mítico

Panel web de administración para el bot de Telegram Mundo Mítico, construido con Flask.

## 🚀 Características

- **Flask**: Framework web ligero y rápido
- **MongoDB**: Base de datos asíncrona con Motor
- **Tailwind CSS**: Diseño moderno y responsive
- **Autenticación**: Sistema de sesiones para administradores
- **Monitoreo**: Estadísticas en tiempo real
- **Gestión**: Procesamiento de depósitos y retiros

## 🛠️ Tecnologías

- **Backend**: Flask + Gunicorn
- **Base de Datos**: MongoDB Atlas
- **Frontend**: HTML + JavaScript + Tailwind CSS
- **Autenticación**: Sistema de sesiones con cookies

## 📋 Requisitos

- Python 3.11+
- MongoDB Atlas (conexión configurada)
- ID de administrador de Telegram

## 🔧 Instalación

1. **Clonar el repositorio:**
```bash
git clone <repo-url>
cd admin_panel
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
# Crear archivo .env (opcional)
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=mundomi
ADMIN_IDS=7828962018
ADMIN_SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

4. **Ejecutar el panel:**
```bash
python app.py
```

## 🌐 Despliegue

### Railway (Recomendado)

1. **Conectar repositorio** a Railway
2. **Configurar variables de entorno** en Railway
3. **Deploy automático** al hacer push

### Variables de entorno en Railway:

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

### Dashboard
- **Estadísticas en tiempo real**: Usuarios, depósitos, retiros, volumen
- **Depósitos pendientes**: Lista con opciones de procesar/cancelar
- **Retiros pendientes**: Lista con opciones de procesar/cancelar

### API Endpoints

- `GET /` - Redirección a login o dashboard
- `GET /login` - Página de login
- `POST /login` - Autenticación
- `GET /dashboard` - Panel principal
- `GET /logout` - Cerrar sesión
- `GET /health` - Health check

#### API Protegida (requiere autenticación):
- `GET /api/stats` - Estadísticas del sistema
- `GET /api/deposits` - Depósitos pendientes
- `GET /api/withdrawals` - Retiros pendientes
- `POST /api/process-deposit` - Procesar depósito
- `POST /api/process-withdrawal` - Procesar retiro
- `POST /api/cancel-deposit` - Cancelar depósito
- `POST /api/cancel-withdrawal` - Cancelar retiro

## 🔗 Integración con el Bot

El panel se conecta a la misma base de datos MongoDB Atlas que el bot:

1. **Base de datos compartida**: `mundomi`
2. **Colecciones principales**:
   - `users` - Usuarios del bot
   - `deposits` - Depósitos (status: pending/completed/cancelled)
   - `withdrawals` - Retiros (status: pending/completed/cancelled)
   - `admin_actions` - Log de acciones de administradores

3. **Sincronización**: Los cambios en el panel se reflejan inmediatamente en el bot

## 🎨 Diseño

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

El panel registra todas las acciones de administración en la colección `admin_actions`:

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

### Error de conexión a MongoDB
- Verificar `MONGO_URI` y credenciales
- Comprobar que la IP esté en whitelist de MongoDB Atlas

### Error de autenticación
- Verificar que el `ADMIN_IDS` contenga el ID correcto
- Limpiar cookies del navegador

### Error de puerto
- Verificar que el puerto no esté en uso
- Usar variable `PORT` en Railway

## 📞 Soporte

Para problemas o consultas:
1. Revisar logs en Railway
2. Verificar configuración de variables de entorno
3. Comprobar conexión a MongoDB Atlas

---

**Desarrollado para Mundo Mítico Bot** 🤖 