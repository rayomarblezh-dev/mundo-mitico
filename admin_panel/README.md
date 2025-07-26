# Panel de Administración - Mundo Mítico

Panel web de administración integrado con el bot de Telegram Mundo Mítico.

## 🚀 Características

- **Dashboard responsive** con estadísticas en tiempo real
- **Gestión de depósitos** - Procesar y cancelar depósitos pendientes
- **Gestión de retiros** - Procesar y cancelar retiros pendientes
- **Diseño moderno** con Tailwind CSS y tema oscuro
- **Autenticación segura** por ID de administrador
- **Integración completa** con la base de datos del bot
- **Despliegue independiente** o integrado con el bot

## 🛠️ Tecnologías

- **Backend**: Flask + Motor (MongoDB async)
- **Frontend**: HTML + Tailwind CSS + JavaScript
- **Base de datos**: MongoDB (misma que el bot)
- **Autenticación**: Sesiones Flask
- **Producción**: Gunicorn + Nginx

## 📋 Configuración

### Variables de Entorno

Crea un archivo `.env` en la carpeta `admin_panel`:

```env
# Configuración del panel de administración
ADMIN_IDS=7828962018,1234567890
ADMIN_SECRET_KEY=tu-clave-secreta-super-segura
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# Base de datos (usar la misma que el bot)
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=mundo_mitico
```

### IDs de Administradores

Los `ADMIN_IDS` son los IDs de Telegram de los usuarios que pueden acceder al panel. Separa múltiples IDs con comas.

## 🚀 Uso

### Opción 1: Integrado con el Bot

El panel se inicia automáticamente junto con el bot:

```bash
python main.py
```

**Acceso desde el bot:**
- Los administradores pueden usar el comando `/admin` en Telegram
- El bot enviará un botón con el enlace directo al panel

### Opción 2: Independiente

Ejecutar solo el panel de administración:

```bash
cd admin_panel
python app.py
```

### Opción 3: Script de Despliegue

Usar el script automatizado:

```bash
cd admin_panel
chmod +x deploy.sh
./deploy.sh
```

### Acceso

1. **Desde Telegram:** Usa el comando `/admin` (solo administradores)
2. **Directo:** Abre tu navegador en: `http://localhost:5000`
3. Ingresa tu ID de administrador de Telegram
4. ¡Listo! Ya puedes gestionar depósitos y retiros

### Puertos

- **Bot API**: Puerto configurado en `API_PORT` (por defecto 8000)
- **Panel Admin**: Puerto 5000 (configurable con `FLASK_PORT`)

## 📊 Funcionalidades

### Dashboard Principal
- Estadísticas generales del sistema
- Usuarios totales y activos
- Volumen total de transacciones
- Depósitos y retiros totales

### Gestión de Depósitos
- Ver depósitos pendientes
- Procesar depósitos (agregar balance al usuario)
- Cancelar depósitos
- Ver detalles: ID, usuario, cantidad, red, hash

### Gestión de Retiros
- Ver retiros pendientes
- Marcar retiros como procesados
- Cancelar retiros (devolver fondos al usuario)
- Ver detalles: ID, usuario, cantidad, wallet

## 🔒 Seguridad

- **Autenticación**: Solo IDs de administrador autorizados
- **Sesiones**: Manejo seguro de sesiones con Flask
- **Logs**: Todas las acciones se registran en la base de datos
- **Validación**: Validación de datos en frontend y backend
- **Health Check**: Endpoint `/health` para monitoreo

## 🎨 Personalización

### Colores y Estilo
El panel usa una paleta de colores oscura personalizable en `templates/dashboard.html` y `templates/login.html`.

### Fuente
Se usa la fuente Poppins de Google Fonts. Puedes cambiarla modificando el `fontFamily` en la configuración de Tailwind.

## 🌐 Despliegue en Producción

### Railway (Recomendado - Gratis)

1. **Conectar repositorio** a Railway
2. **Configurar variables** de entorno
3. **Desplegar automáticamente**

### Render (Alternativa - Gratis)

1. **Crear Web Service**
2. **Configurar build y start commands**
3. **Configurar variables** de entorno

### VPS (DigitalOcean, AWS, etc.)

1. **Usar script de despliegue**: `./deploy.sh production`
2. **Configurar Nginx** como proxy reverso
3. **Configurar SSL** con Let's Encrypt

## 🐛 Solución de Problemas

### Panel no carga
- Verifica que el puerto 5000 esté disponible
- Revisa los logs para errores
- Confirma que las variables de entorno estén configuradas

### Error de autenticación
- Verifica que tu ID esté en `ADMIN_IDS`
- Asegúrate de que `ADMIN_SECRET_KEY` esté configurado

### Error de base de datos
- Confirma que MongoDB esté ejecutándose
- Verifica la conexión en `MONGO_URI`
- Revisa que la base de datos exista

### Health Check
```bash
curl http://localhost:5000/health
```

## 📝 Logs

Todas las acciones administrativas se registran en la colección `logs` de MongoDB con:
- ID del administrador
- Tipo de acción
- ID del usuario afectado (si aplica)
- Detalles adicionales
- Timestamp

## 🔄 Actualizaciones

### Integrado con Bot
1. Detén el bot
2. Actualiza los archivos del panel
3. Reinicia el bot
4. El panel se actualizará automáticamente

### Independiente
1. Actualiza los archivos
2. Reinicia el servicio
3. ¡Listo!

## 📁 Estructura de Archivos

```
admin_panel/
├── app.py              # Aplicación principal Flask
├── wsgi.py             # Servidor WSGI para producción
├── requirements.txt    # Dependencias Python
├── Procfile           # Configuración para Railway/Heroku
├── railway.json       # Configuración específica Railway
├── runtime.txt        # Versión de Python
├── deploy.sh          # Script de despliegue
├── templates/         # Plantillas HTML
│   ├── login.html     # Página de login
│   └── dashboard.html # Dashboard principal
└── README.md          # Esta documentación
``` 