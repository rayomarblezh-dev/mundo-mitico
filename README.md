# 🌍 Mundo Mítico - Bot de Telegram

Un bot de Telegram épico que te sumerge en un universo de criaturas legendarias, exploraciones mágicas y economía virtual basada en TON.

## 🚀 Características Principales

### 🐾 Sistema de Criaturas
- **11 criaturas únicas** con diferentes rarezas y usos
- **Sistema de captura** y colección
- **Criaturas básicas**: Hadas, Magos, Orcos, Elfos, Gnomos
- **Criaturas intermedias**: Dragones, Unicornios, Genios, Gremnlis
- **Criaturas avanzadas**: Kraken, Licántropos

### 🎨 Sistema de NFTs
- **3 NFTs únicos** con ganancias diarias
- **Moguri-NFT**: 5.0 TON (0.1 TON/día)
- **Gargola-NFT**: 10.0 TON (0.25 TON/día)
- **Ghost-NFT**: 25.0 TON (0.75 TON/día)
- **Duración limitada**: 30 días por NFT

### 🌍 Sistema de Exploración
- **Caja Sorpresa**: Descubre tesoros aleatorios (0.05 TON)
- **Pelea**: Enfréntate en combate (requiere 3 Licántropos)
- **Expedición**: Explora territorios (requiere 1 Elfo + 1 Genio + 1 Orco)
- **Capturar**: Atrapa bestias míticas (requiere 1 Licántropo + 2 Orcos)
- **Sistema de cooldowns** para balancear el juego

### 👛 Sistema de Wallet
- **Depósitos**: USDT TON, USDT TRC20, TON
- **Retiros**: Mínimo 1.1 TON con comisión del 10%
- **Verificación de transacciones** con hashes
- **Sistema de estados** para transacciones

### 📋 Sistema de Tareas
- **Enlace de referido en bio**: Recompensas por 3 y 7 días
- **Nombre con "Mundo Mitico"**: Recompensas por 10 días
- **Verificación automática** de cumplimiento
- **Sistema de recompensas** progresivas

### 👥 Sistema de Referidos
- **Recompensas por invitaciones**: 1 Hada cada 10 referidos
- **Recompensas por actividad**: 1 Elfo por referido activo
- **Seguimiento automático** de referidos
- **Sistema de notificaciones**

## 🛠️ Tecnologías Utilizadas

- **Python 3.11+**
- **aiogram 3.21.0** - Framework de Telegram Bot API
- **MongoDB** - Base de datos NoSQL
- **motor** - Driver asíncrono para MongoDB
- **httpx** - Cliente HTTP asíncrono
- **Docker** - Containerización

## 📦 Instalación

### Prerrequisitos
- Python 3.11 o superior
- MongoDB (local o en la nube)
- Token de bot de Telegram

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd mundo-mitico
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables
Editar `config/config.py`:
```python
BOT_TOKEN = "tu_token_aqui"
MONGO_URI = "tu_mongodb_uri"
DB_NAME = "mundom"
ADMIN_IDS = [tu_user_id]
```

### 5. Ejecutar validador
```bash
python utils/validator.py
```

### 6. Iniciar el bot
```bash
python main.py
```

## 🏗️ Estructura del Proyecto

```
mundo-mitico/
├── config/
│   ├── __init__.py
│   └── config.py          # Configuración principal
├── images/
│   ├── gargola.jpg        # Imágenes de NFTs
│   ├── ghost.jpg
│   └── moguri.jpg
├── modules/
│   ├── __init__.py
│   ├── bot.py             # Configuración del bot
│   ├── commands.py        # Registro de comandos
│   ├── constants.py       # Constantes centralizadas
│   ├── criaturas.py       # Sistema de criaturas
│   ├── explorar.py        # Sistema de exploración
│   ├── inventario.py      # Sistema de inventario
│   ├── nfts.py           # Sistema de NFTs
│   ├── referidos.py      # Sistema de referidos
│   ├── recompensas.py    # Sistema de recompensas
│   ├── start.py          # Handler principal
│   ├── tareas.py         # Sistema de tareas
│   ├── tienda.py         # Sistema de tienda
│   └── wallet.py         # Sistema de wallet
├── utils/
│   ├── __init__.py
│   ├── database.py       # Funciones de base de datos
│   ├── logging_config.py # Configuración de logging
│   └── validator.py      # Validador del proyecto
├── main.py               # Punto de entrada
├── requirements.txt      # Dependencias
├── Dockerfile           # Configuración Docker
└── README.md            # Documentación
```

## 🔧 Configuración

### Variables de Entorno
- `BOT_TOKEN`: Token de tu bot de Telegram
- `MONGO_URI`: URI de conexión a MongoDB
- `DB_NAME`: Nombre de la base de datos
- `ADMIN_IDS`: Lista de IDs de administradores

### Configuración del Sistema
```python
SISTEMA_CONFIG = {
    "min_deposito": 0.5,        # Depósito mínimo
    "min_retiro": 1.1,          # Retiro mínimo
    "comision_retiro": 0.1,     # Comisión de retiro (10%)
    "tiempo_procesamiento": "24-48h"
}
```

## 🚀 Despliegue

### Docker
```bash
docker build -t mundo-mitico .
docker run -d mundo-mitico
```

### Railway
El proyecto incluye `railway.json` para despliegue automático en Railway.

### Manual
```bash
python main.py
```

## 📊 Monitoreo

### Logs
El sistema utiliza logging centralizado con diferentes niveles:
- `INFO`: Información general
- `WARNING`: Advertencias
- `ERROR`: Errores
- `CRITICAL`: Errores críticos

### Métricas
- Usuarios activos
- Transacciones procesadas
- NFTs activos
- Referidos totales

## 🔒 Seguridad

- **Validación de transacciones** con hashes
- **Verificación de permisos** de administrador
- **Sanitización de inputs** de usuario
- **Logging de acciones** críticas
- **Cooldowns** para prevenir spam

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Canal de Telegram**: [@MundoMitico](https://t.me/MundoMitico)
- **Soporte**: [@wolfpromot](http://t.me/wolfpromot)
- **Issues**: Usa la sección de Issues de GitHub

## 🎯 Roadmap

- [ ] Sistema de clanes/guildas
- [ ] Eventos temporales
- [ ] Marketplace de criaturas
- [ ] Sistema de rankings
- [ ] Integración con más blockchains
- [ ] App móvil nativa

---

**¡Únete a la aventura en Mundo Mítico! 🌍✨** 