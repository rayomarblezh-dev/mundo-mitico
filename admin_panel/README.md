# Panel de Administración - Mundo Mítico

Panel web de administración integrado con el bot de Telegram Mundo Mítico.

## 🚀 Características

- **Dashboard responsive** con estadísticas en tiempo real
- **Gestión de depósitos** - Procesar y cancelar depósitos pendientes
- **Gestión de retiros** - Procesar y cancelar retiros pendientes
- **Diseño moderno** con Tailwind CSS y tema oscuro
- **Autenticación segura** por ID de administrador
- **Integración completa** con la base de datos del bot

## 🛠️ Tecnologías

- **Backend**: Flask + Motor (MongoDB async)
- **Frontend**: HTML + Tailwind CSS + JavaScript
- **Base de datos**: MongoDB (misma que el bot)
- **Autenticación**: Sesiones Flask

## 📋 Configuración

### Variables de Entorno

Agrega estas variables a tu archivo `.env`:

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

### Inicio Automático

El panel se inicia automáticamente junto con el bot cuando ejecutas:

```bash
python main.py
```

### Acceso

1. Abre tu navegador en: `http://localhost:5000`
2. Ingresa tu ID de administrador de Telegram
3. ¡Listo! Ya puedes gestionar depósitos y retiros

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

## 🎨 Personalización

### Colores y Estilo
El panel usa una paleta de colores oscura personalizable en `templates/dashboard.html` y `templates/login.html`.

### Fuente
Se usa la fuente Poppins de Google Fonts. Puedes cambiarla modificando el `fontFamily` en la configuración de Tailwind.

## 🐛 Solución de Problemas

### Panel no carga
- Verifica que el puerto 5000 esté disponible
- Revisa los logs del bot para errores de Flask
- Confirma que las variables de entorno estén configuradas

### Error de autenticación
- Verifica que tu ID esté en `ADMIN_IDS`
- Asegúrate de que `ADMIN_SECRET_KEY` esté configurado

### Error de base de datos
- Confirma que MongoDB esté ejecutándose
- Verifica la conexión en `MONGO_URI`
- Revisa que la base de datos exista

## 📝 Logs

Todas las acciones administrativas se registran en la colección `logs` de MongoDB con:
- ID del administrador
- Tipo de acción
- ID del usuario afectado (si aplica)
- Detalles adicionales
- Timestamp

## 🔄 Actualizaciones

Para actualizar el panel:
1. Detén el bot
2. Actualiza los archivos del panel
3. Reinicia el bot
4. El panel se actualizará automáticamente 