# 🚀 Guía de Despliegue - Panel de Administración

## 🌐 Opciones de Despliegue

### 1. Railway (Recomendado - Gratis)

**Ventajas:**
- ✅ Gratis para proyectos pequeños
- ✅ Despliegue automático desde GitHub
- ✅ Dominio personalizado incluido
- ✅ Variables de entorno fáciles de configurar
- ✅ SSL automático

**Pasos:**

1. **Crear cuenta en Railway:**
   - Ve a [railway.app](https://railway.app)
   - Conecta tu cuenta de GitHub

2. **Crear nuevo proyecto:**
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Selecciona tu repositorio

3. **Configurar variables de entorno:**
   ```env
   MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/mundo_mitico
   DATABASE_NAME=mundo_mitico
   ADMIN_IDS=7828962018
   ADMIN_SECRET_KEY=tu-clave-secreta-super-segura
   FLASK_DEBUG=False
   ```

4. **Desplegar:**
   - Railway detectará automáticamente que es una app Python
   - Se desplegará automáticamente

5. **Dominio personalizado:**
   - Ve a "Settings" → "Domains"
   - Agrega tu dominio personalizado
   - Configura los DNS según las instrucciones

### 2. Render (Alternativa - Gratis)

**Pasos:**

1. **Crear cuenta en Render:**
   - Ve a [render.com](https://render.com)
   - Conecta tu GitHub

2. **Crear Web Service:**
   - Click en "New" → "Web Service"
   - Conecta tu repositorio
   - Configura:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn wsgi:app`

3. **Variables de entorno:**
   ```env
   MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/mundo_mitico
   DATABASE_NAME=mundo_mitico
   ADMIN_IDS=7828962018
   ADMIN_SECRET_KEY=tu-clave-secreta-super-segura
   ```

### 3. Heroku (Pago)

**Pasos:**

1. **Instalar Heroku CLI:**
   ```bash
   # Windows
   winget install --id=Heroku.HerokuCLI
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Login y crear app:**
   ```bash
   heroku login
   heroku create tu-app-name
   ```

3. **Configurar variables:**
   ```bash
   heroku config:set MONGO_URI="mongodb+srv://..."
   heroku config:set ADMIN_IDS="7828962018"
   heroku config:set ADMIN_SECRET_KEY="tu-clave-secreta"
   ```

4. **Desplegar:**
   ```bash
   git add .
   git commit -m "Deploy admin panel"
   git push heroku main
   ```

### 4. VPS (DigitalOcean, AWS, etc.)

**Pasos:**

1. **Configurar servidor:**
   ```bash
   # Actualizar sistema
   sudo apt update && sudo apt upgrade -y
   
   # Instalar Python y dependencias
   sudo apt install python3 python3-pip nginx -y
   ```

2. **Clonar repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo/admin_panel
   ```

3. **Instalar dependencias:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configurar Gunicorn:**
   ```bash
   # Crear servicio systemd
   sudo nano /etc/systemd/system/admin-panel.service
   ```

   ```ini
   [Unit]
   Description=Admin Panel
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/admin_panel
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:admin-panel.sock -m 007 wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```

5. **Configurar Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/admin-panel
   ```

   ```nginx
   server {
       listen 80;
       server_name tu-dominio.com;

       location / {
           include proxy_params;
           proxy_pass http://unix:/path/to/admin_panel/admin-panel.sock;
       }
   }
   ```

6. **Activar y iniciar:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/admin-panel /etc/nginx/sites-enabled
   sudo systemctl start admin-panel
   sudo systemctl enable admin-panel
   sudo systemctl restart nginx
   ```

## 🔧 Configuración de Base de Datos

### MongoDB Atlas (Recomendado)

1. **Crear cluster en MongoDB Atlas:**
   - Ve a [mongodb.com/atlas](https://mongodb.com/atlas)
   - Crea cuenta gratuita
   - Crea un cluster (gratis)

2. **Configurar red:**
   - Ve a "Network Access"
   - Agrega IP `0.0.0.0/0` para acceso desde cualquier lugar

3. **Crear usuario:**
   - Ve a "Database Access"
   - Crea usuario con permisos de lectura/escritura

4. **Obtener conexión:**
   - Ve a "Connect"
   - Selecciona "Connect your application"
   - Copia la URL de conexión

## 🔒 Seguridad en Producción

### Variables de Entorno Críticas

```env
# OBLIGATORIAS
ADMIN_SECRET_KEY=clave-super-segura-de-al-menos-32-caracteres
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/mundo_mitico
ADMIN_IDS=7828962018

# OPCIONALES
CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
FLASK_DEBUG=False
```

### Recomendaciones de Seguridad

1. **Clave secreta fuerte:**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **HTTPS obligatorio:**
   - Configura SSL en tu proveedor
   - Redirige HTTP a HTTPS

3. **Firewall:**
   - Solo puertos 80, 443, 22 abiertos
   - Bloquear acceso directo a MongoDB

4. **Backups:**
   - Configura backups automáticos de MongoDB
   - Guarda copias de las variables de entorno

## 🌍 Dominio Personalizado

### Configuración DNS

1. **Registrar dominio:**
   - Namecheap, GoDaddy, Google Domains, etc.

2. **Configurar DNS:**
   ```
   Tipo: A
   Nombre: @
   Valor: IP_DEL_SERVIDOR
   
   Tipo: CNAME
   Nombre: www
   Valor: tu-dominio.com
   ```

3. **SSL automático:**
   - Railway/Render: Automático
   - VPS: Usar Let's Encrypt

## 📊 Monitoreo

### Health Check

El panel incluye un endpoint de health check:
```
GET https://tu-dominio.com/health
```

### Logs

- **Railway/Render:** Logs automáticos en el dashboard
- **VPS:** `sudo journalctl -u admin-panel -f`

## 🔄 Actualizaciones

### Despliegue Automático

1. **Railway/Render:** Push a GitHub = deploy automático
2. **VPS:** Script de actualización:

```bash
#!/bin/bash
cd /path/to/admin_panel
git pull origin main
sudo systemctl restart admin-panel
```

## 🆘 Solución de Problemas

### Error de Conexión a MongoDB
```bash
# Verificar conexión
python3 -c "
import motor.motor_asyncio
import asyncio
async def test():
    client = motor.motor_asyncio.AsyncIOMotorClient('MONGO_URI')
    await client.admin.command('ping')
    print('✅ Conexión exitosa')
asyncio.run(test())
"
```

### Error de Puerto
```bash
# Verificar puerto en uso
sudo netstat -tlnp | grep :5000
```

### Error de Permisos
```bash
# Corregir permisos
sudo chown -R www-data:www-data /path/to/admin_panel
sudo chmod -R 755 /path/to/admin_panel
``` 