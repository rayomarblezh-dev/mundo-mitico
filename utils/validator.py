"""
Validador de integridad del proyecto Mundo Mítico
Verifica que todas las importaciones, configuraciones y dependencias estén correctas
"""

import os
import sys
import importlib
import logging

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any

# Configurar logging básico para el validador
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

class ProjectValidator:
    """Clase para validar la integridad del proyecto"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def add_error(self, message: str):
        """Agrega un error a la lista"""
        self.errors.append(message)
        logger.error(f"❌ {message}")
        
    def add_warning(self, message: str):
        """Agrega una advertencia a la lista"""
        self.warnings.append(message)
        logger.warning(f"⚠️ {message}")
        
    def add_success(self, message: str):
        """Agrega un éxito a la lista"""
        self.success_count += 1
        logger.info(f"✅ {message}")
        
    def validate_imports(self) -> bool:
        """Valida que todas las importaciones funcionen correctamente"""
        logger.info("🔍 Validando importaciones...")
        
        modules_to_test = [
            "aiogram",
            "motor",
            "httpx",
            "bson",
            "datetime",
            "logging",
            "os",
            "sys",
            "typing"
        ]
        
        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                self.add_success(f"Importación exitosa: {module_name}")
            except ImportError as e:
                self.add_error(f"Error importando {module_name}: {e}")
                
        # Validar módulos internos
        internal_modules = [
            "config.config",
            "utils.database",
            "modules.constants",
            "modules.bot",
            "modules.commands",
            "modules.start",
            "modules.wallet",
            "modules.tienda",
            "modules.inventario",
            "modules.explorar",
            "modules.criaturas",
            "modules.nfts",
            "modules.tareas",
            "modules.referidos",
            "modules.recompensas"
        ]
        
        for module_name in internal_modules:
            try:
                importlib.import_module(module_name)
                self.add_success(f"Importación exitosa: {module_name}")
            except ImportError as e:
                self.add_error(f"Error importando {module_name}: {e}")
                
        return len(self.errors) == 0
        
    def validate_config(self) -> bool:
        """Valida la configuración del proyecto"""
        logger.info("🔍 Validando configuración...")
        
        try:
            from config.config import BOT_TOKEN, MONGO_URI, DB_NAME
            from config.config import MIN_DEPOSIT, MIN_WITHDRAWAL, WITHDRAWAL_FEE
            
            # Validar BOT_TOKEN
            if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
                self.add_error("BOT_TOKEN no configurado correctamente")
            else:
                self.add_success("BOT_TOKEN configurado")
                
            # Validar MONGO_URI
            if not MONGO_URI or MONGO_URI == "YOUR_MONGO_URI":
                self.add_error("MONGO_URI no configurado correctamente")
            else:
                self.add_success("MONGO_URI configurado")
                
            # Validar DB_NAME
            if not DB_NAME:
                self.add_error("DB_NAME no configurado")
            else:
                self.add_success("DB_NAME configurado")
                
            # Validar configuraciones de constantes
            if not CRIATURAS_CONFIG:
                self.add_error("CRIATURAS_CONFIG vacío")
            else:
                self.add_success(f"CRIATURAS_CONFIG: {len(CRIATURAS_CONFIG)} criaturas")
                
            if not NFTS_CONFIG:
                self.add_error("NFTS_CONFIG vacío")
            else:
                self.add_success(f"NFTS_CONFIG: {len(NFTS_CONFIG)} NFTs")
                
            if not SISTEMA_CONFIG:
                self.add_error("SISTEMA_CONFIG vacío")
            else:
                self.add_success("SISTEMA_CONFIG configurado")
                
        except ImportError as e:
            self.add_error(f"Error importando configuración: {e}")
            
        return len(self.errors) == 0
        
    def validate_files(self) -> bool:
        """Valida que todos los archivos necesarios existan"""
        logger.info("🔍 Validando archivos...")
        
        required_files = [
            "main.py",
            "requirements.txt",
            "config/config.py",
            "utils/database.py",
            "utils/logging_config.py",
            "modules/bot.py",
            "modules/commands.py",
            "modules/constants.py",
            "modules/start.py",
            "modules/wallet.py",
            "modules/tienda.py",
            "modules/inventario.py",
            "modules/explorar.py",
            "modules/criaturas.py",
            "modules/nfts.py",
            "modules/tareas.py",
            "modules/referidos.py",
            "modules/recompensas.py"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.add_success(f"Archivo encontrado: {file_path}")
            else:
                self.add_error(f"Archivo faltante: {file_path}")
                
        # Validar imágenes de NFTs
        nft_images = ["images/moguri.jpg", "images/gargola.jpg", "images/ghost.jpg"]
        for image_path in nft_images:
            if os.path.exists(image_path):
                self.add_success(f"Imagen NFT encontrada: {image_path}")
            else:
                self.add_warning(f"Imagen NFT faltante: {image_path}")
                
        return len(self.errors) == 0
        
    def validate_database_connection(self) -> bool:
        """Valida la conexión a la base de datos"""
        logger.info("🔍 Validando conexión a base de datos...")
        
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            from config.config import MONGO_URI
            
            # Intentar conectar a MongoDB
            client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Verificar conexión
            client.admin.command('ping')
            self.add_success("Conexión a MongoDB exitosa")
            client.close()
            return True
            
        except Exception as e:
            self.add_error(f"Error conectando a MongoDB: {e}")
            return False
            
    def run_full_validation(self) -> Dict[str, Any]:
        """Ejecuta todas las validaciones"""
        logger.info("🚀 Iniciando validación completa del proyecto...")
        
        results = {
            "imports": self.validate_imports(),
            "config": self.validate_config(),
            "files": self.validate_files(),
            "database": self.validate_database_connection(),
            "errors": self.errors,
            "warnings": self.warnings,
            "success_count": self.success_count
        }
        
        # Resumen final
        total_checks = results["success_count"] + len(results["errors"]) + len(results["warnings"])
        
        logger.info(f"\n📊 RESUMEN DE VALIDACIÓN:")
        logger.info(f"✅ Éxitos: {results['success_count']}")
        logger.info(f"❌ Errores: {len(results['errors'])}")
        logger.info(f"⚠️ Advertencias: {len(results['warnings'])}")
        logger.info(f"📈 Total de verificaciones: {total_checks}")
        
        if results["errors"]:
            logger.error("\n❌ ERRORES ENCONTRADOS:")
            for error in results["errors"]:
                logger.error(f"  • {error}")
                
        if results["warnings"]:
            logger.warning("\n⚠️ ADVERTENCIAS:")
            for warning in results["warnings"]:
                logger.warning(f"  • {warning}")
                
        if not results["errors"]:
            logger.info("\n🎉 ¡Validación completada exitosamente!")
        else:
            logger.error("\n💥 Validación falló. Corrige los errores antes de continuar.")
            
        return results

def main():
    """Función principal para ejecutar la validación"""
    validator = ProjectValidator()
    results = validator.run_full_validation()
    
    # Retornar código de salida apropiado
    if results["errors"]:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 