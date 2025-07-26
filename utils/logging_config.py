"""
Configuración centralizada de logging para el bot Mundo Mítico
"""

import logging
import sys
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Configura el sistema de logging para toda la aplicación
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo donde guardar los logs (opcional)
        format_string: Formato personalizado para los logs (opcional)
    """
    
    # Formato por defecto
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    # Configurar el nivel de logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar el handler básico
    handlers = []
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # Handler para archivo (si se especifica)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(numeric_level)
            file_formatter = logging.Formatter(format_string)
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(f"Error configurando logging a archivo: {e}")
    
    # Configurar el logger raíz
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=handlers,
        force=True
    )
    
    # Configurar loggers específicos
    loggers_to_configure = [
        'aiogram',
        'motor',
        'httpx',
        'asyncio'
    ]
    
    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
    
    # Log de inicio
    logging.info(f"✅ Sistema de logging configurado - Nivel: {level}")

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para un módulo específico
    
    Args:
        name: Nombre del módulo (ej: 'modules.wallet')
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)

# Configuración por defecto al importar el módulo
if __name__ != "__main__":
    setup_logging() 