# Constantes para el bot Mundo Mítico
import os
from aiogram.types import FSInputFile

# Emojis principales
EMOJI_DEPOSITO = "📥"
EMOJI_RETIRO = "📤"
EMOJI_OK = "✅"
EMOJI_CANCEL = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_MONEY = "💰"
EMOJI_USER = "👤"
EMOJI_ADMIN = "🔧"
EMOJI_STATS = "📊"
EMOJI_SEARCH = "🔍"
EMOJI_HISTORY = "📋"
EMOJI_TIME = "⏰"
EMOJI_NETWORK = "🌐"
EMOJI_WALLET = "👛"

# Textos para depósitos y retiros
TEXTO_DEPOSITO_PENDIENTE = "📥 Depósito Pendiente"
TEXTO_RETIRO_PENDIENTE = "📤 Retiro Pendiente"

# Mensajes de estado
MENSAJE_ACCESO_DENEGADO = "❌ Acceso Denegado"
MENSAJE_OPERACION_EXITOSA = "✅ Operación Exitosa"
MENSAJE_ERROR_GENERICO = "❌ Error en la operación"
MENSAJE_DATOS_INCOMPLETOS = "⚠️ Datos incompletos"
MENSAJE_USUARIO_NO_ENCONTRADO = "❌ Usuario no encontrado"

# Configuración de paginación
ITEMS_POR_PAGINA = 5
MAX_ITEMS_BUSQUEDA = 20

# Estados de operaciones
ESTADO_PENDIENTE = "pendiente"
ESTADO_COMPLETADO = "completado"
ESTADO_CANCELADO = "cancelado"
ESTADO_RECHAZADO = "rechazado"

# Tipos de operaciones
TIPO_DEPOSITO = "deposito"
TIPO_RETIRO = "retiro"
TIPO_ADMIN = "admin"

# Configuración de logs
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"

# Formato de fechas
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"
FORMATO_FECHA_CORTA = "%Y-%m-%d"

# Configuración de monedas
MONEDA_PRINCIPAL = "TON"
MONEDA_USDT = "USDT"
MONEDA_TRX = "TRX"

# Redes soportadas
REDES_SOPORTADAS = {
    "usdt_ton": "USDT TON",
    "usdt_trc20": "USDT TRC20", 
    "ton": "TON"
}

# Configuración de cooldowns (en horas)
COOLDOWNS_EXPLORAR = {
    "pelea": 48,
    "expedicion": 48,
    "capturar": 24
}

# Configuración de recompensas
RECOMPENSAS_CAJA_SORPRESA = {
    "nada": {"probabilidad": 50, "mensaje": "❌ No encontraste nada especial esta vez."},
    "hada": {"probabilidad": 30, "mensaje": "🎉 ¡Encontraste 1 Hada!", "item": "hada", "cantidad": 1},
    "elfo": {"probabilidad": 10, "mensaje": "🎉 ¡Encontraste 1 Elfo!", "item": "elfo", "cantidad": 1},
    "gnomo": {"probabilidad": 5, "mensaje": "🎉 ¡Encontraste 1 Gnomo!", "item": "gnomo", "cantidad": 1},
    "orco": {"probabilidad": 1, "mensaje": "🎉 ¡Encontraste 1 Orco!", "item": "orco", "cantidad": 1}
}

# =========================
# CONFIGURACIÓN DE INVENTARIO CENTRALIZADA
# =========================

# Configuración de criaturas (sincronizada con criaturas.py)
CRIATURAS_CONFIG = {
    "hada": {
        "emoji": "🧚‍♀️",
        "nombre": "Hada",
        "precio": 0.10,
        "desc": "Seres mágicos de los bosques encantados que traen buena fortuna y protección a sus dueños.",
        "categoria": "Básica",
        "uso": "Explorar, Caja Sorpresa",
        "ganancia_diaria": 0.0  # Las criaturas no generan ganancias diarias
    },
    "mago": {
        "emoji": "🧙‍♂️",
        "nombre": "Mago",
        "precio": 0.11,
        "desc": "Guardianes ancestrales de la sabiduría mágica, conocedores de los secretos más profundos de la naturaleza.",
        "categoria": "Básica",
        "uso": "Explorar, Expedición",
        "ganancia_diaria": 0.0
    },
    "dragon": {
        "emoji": "🐉",
        "nombre": "Dragón",
        "precio": 0.20,
        "desc": "Majestuosas criaturas de fuego y poder, guardianes de tesoros legendarios y maestros del cielo.",
        "categoria": "Intermedia",
        "uso": "Explorar, Combate",
        "ganancia_diaria": 0.0
    },
    "orco": {
        "emoji": "👹",
        "nombre": "Orco",
        "precio": 0.22,
        "desc": "Guerreros feroces de las montañas oscuras, conocidos por su fuerza bruta y resistencia en batalla.",
        "categoria": "Básica",
        "uso": "Explorar, Expedición, Capturar",
        "ganancia_diaria": 0.0
    },
    "gremnli": {
        "emoji": "👺",
        "nombre": "Gremnli",
        "precio": 0.25,
        "desc": "Tramposos astutos de las cavernas subterráneas, maestros del engaño y la supervivencia.",
        "categoria": "Intermedia",
        "uso": "Explorar, Caja Sorpresa",
        "ganancia_diaria": 0.0
    },
    "unicornio": {
        "emoji": "🦄",
        "nombre": "Unicornio",
        "precio": 0.30,
        "desc": "Criaturas puras y mágicas, símbolos de pureza y poder curativo, guardianes de la luz.",
        "categoria": "Intermedia",
        "uso": "Explorar, Curación",
        "ganancia_diaria": 0.0
    },
    "genio": {
        "emoji": "🧞",
        "nombre": "Genio",
        "precio": 0.40,
        "desc": "Seres de poder ilimitado, capaces de conceder deseos y manipular la realidad misma.",
        "categoria": "Intermedia",
        "uso": "Explorar, Expedición",
        "ganancia_diaria": 0.0
    },
    "kraken": {
        "emoji": "👾",
        "nombre": "Kraken",
        "precio": 1.20,
        "desc": "Titanes del océano profundo, criaturas colosales que gobiernan las aguas más oscuras.",
        "categoria": "Avanzada",
        "uso": "Explorar, Combate naval",
        "ganancia_diaria": 0.0
    },
    "licantropo": {
        "emoji": "🐺",
        "nombre": "Licántropo",
        "precio": 1.00,
        "desc": "Guerreros que se transforman bajo la luna llena, combinando la ferocidad del lobo con la inteligencia humana.",
        "categoria": "Avanzada",
        "uso": "Explorar, Pelea, Capturar",
        "ganancia_diaria": 0.0
    },
    "elfo": {
        "emoji": "🧝‍♀️",
        "nombre": "Elfo",
        "precio": 0.15,
        "desc": "Seres mágicos de los bosques ancestrales, conocedores de la naturaleza y la magia.",
        "categoria": "Básica",
        "uso": "Explorar, Expedición",
        "ganancia_diaria": 0.0
    },
    "gnomo": {
        "emoji": "🧝‍♂️",
        "nombre": "Gnomo",
        "precio": 0.08,
        "desc": "Pequeños seres mágicos expertos en artesanía y minería.",
        "categoria": "Básica",
        "uso": "Explorar, Caja Sorpresa",
        "ganancia_diaria": 0.0
    }
}

# Configuración de NFTs (sincronizada con nfts.py)
NFTS_CONFIG = {
    "moguri": {
        "nombre": "Moguri-NFT",
        "emoji": "💀",
        "precio": 5.0,
        "ganancia_diaria": 0.1,
        "duracion": 30,
        "rareza": "Común",
        "descripcion": "Un NFT misterioso con poderes ancestrales que genera ganancias diarias.",
        "imagen": "moguri.jpg"
    },
    "gargola": {
        "nombre": "Gargola-NFT", 
        "emoji": "🦇",
        "precio": 10.0,
        "ganancia_diaria": 0.25,
        "duracion": 30,
        "rareza": "Común",
        "descripcion": "Un NFT protector con energía mágica que ofrece ganancias superiores.",
        "imagen": "gargola.jpg"
    },
    "ghost": {
        "nombre": "Ghost-NFT",
        "emoji": "👻", 
        "precio": 25.0,
        "ganancia_diaria": 0.75,
        "duracion": 30,
        "rareza": "Raro",
        "descripcion": "Un NFT etéreo de rareza superior con poderes sobrenaturales.",
        "imagen": "ghost.jpg"
    }
}

# Mapeo de nombres de NFTs para el inventario
NFT_INVENTARIO_MAP = {
    "moguri": "moguri-nft",
    "gargola": "gargola-nft", 
    "ghost": "ghost-nft"
}

# Tabla de ganancias diarias por NFT (para inventario)
GANANCIAS_DIARIAS_NFTS = {
    "moguri-nft": 0.1,
    "gargola-nft": 0.25,
    "ghost-nft": 0.75,
}

# Configuración de paquete de bienvenida
PAQUETE_BIENVENIDA = {
    "hada": 7,
    "mago": 3,
    "licantropo": 1
}
PAQUETE_PRECIO = 1.5

# Configuración de referidos
REFERIDOS_CONFIG = {
    "hada_cada_10": 10,
    "elfo_por_activo": 1
}

# Configuración de tareas
TAREAS_CONFIG = {
    "mundo_mitico_nombre": {"recompensa": "hada", "cantidad": 1},
    "referido_bio": {"recompensa": "elfo", "cantidad": 1}
}

# Configuración de sistema
SISTEMA_CONFIG = {
    "min_deposito": 0.5,
    "min_retiro": 1.1,
    "comision_retiro": 0.1,
    "tiempo_procesamiento": "24-48h"
}

# =========================
# FUNCIONES DE UTILIDAD PARA INVENTARIO
# =========================

def obtener_emoji_item(item: str) -> str:
    """Obtiene el emoji de un item desde la configuración centralizada"""
    # Buscar en criaturas
    if item in CRIATURAS_CONFIG:
        return CRIATURAS_CONFIG[item]["emoji"]
    
    # Buscar en NFTs
    for nft_key, nft_config in NFTS_CONFIG.items():
        if nft_config["nombre"] == item or item == f"{nft_key}-nft":
            return nft_config["emoji"]
    
    return "📦"  # Emoji por defecto

def obtener_nombre_item(item: str) -> str:
    """Obtiene el nombre legible de un item desde la configuración centralizada"""
    # Buscar en criaturas
    if item in CRIATURAS_CONFIG:
        return CRIATURAS_CONFIG[item]["nombre"]
    
    # Buscar en NFTs
    for nft_key, nft_config in NFTS_CONFIG.items():
        if nft_config["nombre"] == item or item == f"{nft_key}-nft":
            return nft_config["nombre"]
    
    return item.capitalize()  # Capitalizar si no se encuentra

def obtener_ganancia_diaria_item(item: str) -> float:
    """Obtiene la ganancia diaria de un item desde la configuración centralizada"""
    # Buscar en NFTs
    for nft_key, nft_config in NFTS_CONFIG.items():
        if nft_config["nombre"] == item or item == f"{nft_key}-nft":
            return nft_config["ganancia_diaria"]
    
    # Buscar en criaturas (siempre 0)
    if item in CRIATURAS_CONFIG:
        return CRIATURAS_CONFIG[item]["ganancia_diaria"]
    
    return 0.0  # Sin ganancia por defecto

def es_nft(item: str) -> bool:
    """Determina si un item es un NFT"""
    for nft_key, nft_config in NFTS_CONFIG.items():
        if nft_config["nombre"] == item or item == f"{nft_key}-nft":
            return True
    return False

def es_criatura(item: str) -> bool:
    """Determina si un item es una criatura"""
    return item in CRIATURAS_CONFIG

def obtener_categoria_item(item: str) -> str:
    """Obtiene la categoría de un item"""
    if item in CRIATURAS_CONFIG:
        return CRIATURAS_CONFIG[item]["categoria"]
    
    if es_nft(item):
        for nft_key, nft_config in NFTS_CONFIG.items():
            if nft_config["nombre"] == item or item == f"{nft_key}-nft":
                return nft_config["rareza"]
    
    return "Desconocida"

# =========================
# FUNCIONES DE UTILIDAD PARA IMÁGENES DE NFTs
# =========================


def obtener_ruta_imagen_nft(nft_key: str) -> str:
    """Obtiene la ruta completa de la imagen de un NFT"""
    if nft_key not in NFTS_CONFIG:
        return None
    
    imagen_nombre = NFTS_CONFIG[nft_key]["imagen"]
    ruta_completa = os.path.join("images", imagen_nombre)
    return ruta_completa

def verificar_imagen_nft_existe(nft_key: str) -> bool:
    """Verifica si la imagen de un NFT existe en el sistema de archivos"""
    ruta_imagen = obtener_ruta_imagen_nft(nft_key)
    if not ruta_imagen:
        return False
    
    return os.path.exists(ruta_imagen)

def obtener_todas_imagenes_nfts() -> dict:
    """Obtiene un diccionario con todas las rutas de imágenes de NFTs y su estado"""
    imagenes = {}
    
    for nft_key in NFTS_CONFIG.keys():
        ruta_imagen = obtener_ruta_imagen_nft(nft_key)
        existe = os.path.exists(ruta_imagen) if ruta_imagen else False
        
        imagenes[nft_key] = {
            "ruta": ruta_imagen,
            "existe": existe,
            "nombre_archivo": NFTS_CONFIG[nft_key]["imagen"] if existe else None
        }
    
    return imagenes

def verificar_sincronizacion_imagenes() -> dict:
    """Verifica la sincronización completa entre configuración de NFTs e imágenes"""
    resultado = {
        "total_nfts": len(NFTS_CONFIG),
        "imagenes_encontradas": 0,
        "imagenes_faltantes": [],
        "imagenes_extra": [],
        "sincronizado": True
    }
    
    # Verificar imágenes configuradas
    for nft_key, nft_config in NFTS_CONFIG.items():
        imagen_nombre = nft_config["imagen"]
        ruta_completa = os.path.join("images", imagen_nombre)
        
        if os.path.exists(ruta_completa):
            resultado["imagenes_encontradas"] += 1
        else:
            resultado["imagenes_faltantes"].append({
                "nft": nft_key,
                "imagen": imagen_nombre,
                "ruta": ruta_completa
            })
            resultado["sincronizado"] = False
    
    # Verificar imágenes extra en la carpeta
    if os.path.exists("images"):
        archivos_imagen = [f for f in os.listdir("images") 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        imagenes_configuradas = [nft_config["imagen"] for nft_config in NFTS_CONFIG.values()]
        
        for archivo in archivos_imagen:
            if archivo not in imagenes_configuradas:
                resultado["imagenes_extra"].append(archivo)
    
    return resultado

def obtener_imagen_nft_para_telegram(nft_key: str):
    """Obtiene la imagen de un NFT preparada para enviar en Telegram"""
    
    ruta_imagen = obtener_ruta_imagen_nft(nft_key)
    if not ruta_imagen or not os.path.exists(ruta_imagen):
        return None
    
    try:
        return FSInputFile(ruta_imagen)
    except Exception:
        return None 