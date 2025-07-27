import asyncio
import datetime
import logging
from typing import Dict, List
from utils.database import usuarios_col, agregar_balance_usuario, log_action
from modules.constants import NFTS_CONFIG, obtener_ganancia_diaria_item

logger = logging.getLogger(__name__)

class GananciasDiariasManager:
    """Gestor de ganancias diarias automáticas para NFTs"""
    
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def start(self):
        """Inicia el sistema de ganancias diarias"""
        if self.is_running:
            logger.warning("Sistema de ganancias diarias ya está ejecutándose")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._ganancias_loop())
        logger.info("🚀 Sistema de ganancias diarias iniciado")
    
    async def stop(self):
        """Detiene el sistema de ganancias diarias"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Sistema de ganancias diarias detenido")
    
    async def _ganancias_loop(self):
        """Loop principal para calcular ganancias diarias"""
        while self.is_running:
            try:
                # Calcular ganancias diarias
                await self._calcular_ganancias_diarias()
                
                # Verificar NFTs expirados
                await self._verificar_nfts_expirados()
                
                # Esperar hasta la próxima ejecución (24 horas)
                await asyncio.sleep(24 * 60 * 60)  # 24 horas en segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en loop de ganancias diarias: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    async def _calcular_ganancias_diarias(self):
        """Calcula y distribuye las ganancias diarias de todos los usuarios"""
        try:
            logger.info("💰 Calculando ganancias diarias...")
            
            # Obtener todos los usuarios con inventario
            usuarios = usuarios_col.find({"inventario": {"$exists": True, "$ne": {}}})
            
            total_ganancias = 0
            usuarios_procesados = 0
            
            async for usuario in usuarios:
                try:
                    user_id = usuario["user_id"]
                    inventario = usuario.get("inventario", {})
                    
                    # Calcular ganancia total del usuario
                    ganancia_usuario = 0
                    nfts_con_ganancia = []
                    
                    for item, cantidad in inventario.items():
                        if cantidad > 0:
                            ganancia_item = obtener_ganancia_diaria_item(item)
                            if ganancia_item > 0:
                                ganancia_total_item = ganancia_item * cantidad
                                ganancia_usuario += ganancia_total_item
                                nfts_con_ganancia.append({
                                    "item": item,
                                    "cantidad": cantidad,
                                    "ganancia_diaria": ganancia_item,
                                    "ganancia_total": ganancia_total_item
                                })
                    
                    # Aplicar ganancias si el usuario tiene NFTs
                    if ganancia_usuario > 0:
                        await agregar_balance_usuario(user_id, ganancia_usuario)
                        total_ganancias += ganancia_usuario
                        usuarios_procesados += 1
                        
                        # Log de la transacción
                        await log_action(
                            user_id, 
                            "ganancia_diaria_nft", 
                            details={
                                "ganancia_total": ganancia_usuario,
                                "nfts": nfts_con_ganancia,
                                "fecha": datetime.datetime.now()
                            }
                        )
                        
                        # Notificar al usuario (opcional)
                        await self._notificar_ganancia_usuario(user_id, ganancia_usuario, nfts_con_ganancia)
                        
                except Exception as e:
                    logger.error(f"Error procesando ganancias para user_id={user_id}: {e}")
                    continue
            
            logger.info(f"✅ Ganancias diarias calculadas: {usuarios_procesados} usuarios, {total_ganancias:.3f} TON total")
            
        except Exception as e:
            logger.error(f"Error en cálculo de ganancias diarias: {e}")
    
    async def _verificar_nfts_expirados(self):
        """Verifica y desactiva NFTs expirados"""
        try:
            logger.info("⏰ Verificando NFTs expirados...")
            
            # Obtener todos los usuarios con NFTs
            usuarios = usuarios_col.find({"inventario": {"$exists": True, "$ne": {}}})
            
            nfts_expirados = 0
            
            async for usuario in usuarios:
                try:
                    user_id = usuario["user_id"]
                    inventario = usuario.get("inventario", {})
                    fecha_registro = usuario.get("fecha_registro", datetime.datetime.now())
                    
                    # Verificar cada NFT
                    inventario_actualizado = inventario.copy()
                    cambios = False
                    
                    for nft_key, nft_config in NFTS_CONFIG.items():
                        nft_name = nft_config["nombre"]
                        cantidad = inventario.get(nft_name, 0)
                        
                        if cantidad > 0:
                            # Calcular si el NFT ha expirado
                            dias_transcurridos = (datetime.datetime.now() - fecha_registro).days
                            
                            if dias_transcurridos >= nft_config["duracion"]:
                                # NFT expirado - remover del inventario
                                inventario_actualizado[nft_name] = 0
                                cambios = True
                                nfts_expirados += cantidad
                                
                                # Log de expiración
                                await log_action(
                                    user_id,
                                    "nft_expirado",
                                    details={
                                        "nft": nft_name,
                                        "cantidad": cantidad,
                                        "dias_transcurridos": dias_transcurridos,
                                        "duracion": nft_config["duracion"]
                                    }
                                )
                    
                    # Actualizar inventario si hubo cambios
                    if cambios:
                        await usuarios_col.update_one(
                            {"user_id": user_id},
                            {"$set": {"inventario": inventario_actualizado}}
                        )
                        
                        # Notificar al usuario sobre NFTs expirados
                        await self._notificar_nfts_expirados(user_id, inventario, inventario_actualizado)
                        
                except Exception as e:
                    logger.error(f"Error verificando NFTs expirados para user_id={user_id}: {e}")
                    continue
            
            if nfts_expirados > 0:
                logger.info(f"✅ NFTs expirados procesados: {nfts_expirados} NFTs removidos")
            else:
                logger.info("✅ No se encontraron NFTs expirados")
                
        except Exception as e:
            logger.error(f"Error en verificación de NFTs expirados: {e}")
    
    async def _notificar_ganancia_usuario(self, user_id: int, ganancia_total: float, nfts: List[Dict]):
        """Notifica al usuario sobre sus ganancias diarias"""
        try:
            from modules.bot import bot
            
            mensaje = (
                "💰 <b>Ganancias Diarias Recibidas</b>\n\n"
                f"Has recibido <code>{ganancia_total:.3f} TON</code> por tus NFTs:\n\n"
            )
            
            for nft in nfts:
                mensaje += f"• {nft['cantidad']}x {nft['item']}: +{nft['ganancia_total']:.3f} TON\n"
            
            mensaje += f"\n💸 <b>Total: {ganancia_total:.3f} TON</b>\n\n"
            mensaje += "¡Tus NFTs siguen generando ganancias automáticamente!"
            
            await bot.send_message(user_id, mensaje, parse_mode="HTML")
            
        except Exception as e:
            logger.warning(f"No se pudo notificar ganancias a user_id={user_id}: {e}")
    
    async def _notificar_nfts_expirados(self, user_id: int, inventario_anterior: Dict, inventario_nuevo: Dict):
        """Notifica al usuario sobre NFTs expirados"""
        try:
            from modules.bot import bot
            
            nfts_perdidos = []
            for item, cantidad_anterior in inventario_anterior.items():
                cantidad_nueva = inventario_nuevo.get(item, 0)
                if cantidad_anterior > 0 and cantidad_nueva == 0:
                    nfts_perdidos.append(item)
            
            if nfts_perdidos:
                mensaje = (
                    "⏰ <b>NFTs Expirados</b>\n\n"
                    "Los siguientes NFTs han expirado y han sido removidos de tu inventario:\n\n"
                )
                
                for nft in nfts_perdidos:
                    mensaje += f"• {nft}\n"
                
                mensaje += "\n💡 Compra nuevos NFTs para seguir generando ganancias."
                
                await bot.send_message(user_id, mensaje, parse_mode="HTML")
                
        except Exception as e:
            logger.warning(f"No se pudo notificar NFTs expirados a user_id={user_id}: {e}")
    
    async def calcular_ganancias_manual(self, user_id: int) -> Dict:
        """Calcula ganancias manualmente para un usuario específico"""
        try:
            usuario = await usuarios_col.find_one({"user_id": user_id})
            if not usuario:
                return {"ok": False, "msg": "Usuario no encontrado"}
            
            inventario = usuario.get("inventario", {})
            ganancia_total = 0
            nfts_con_ganancia = []
            
            for item, cantidad in inventario.items():
                if cantidad > 0:
                    ganancia_item = obtener_ganancia_diaria_item(item)
                    if ganancia_item > 0:
                        ganancia_total_item = ganancia_item * cantidad
                        ganancia_total += ganancia_total_item
                        nfts_con_ganancia.append({
                            "item": item,
                            "cantidad": cantidad,
                            "ganancia_diaria": ganancia_item,
                            "ganancia_total": ganancia_total_item
                        })
            
            if ganancia_total > 0:
                await agregar_balance_usuario(user_id, ganancia_total)
                
                # Log de la transacción
                await log_action(
                    user_id,
                    "ganancia_manual_nft",
                    details={
                        "ganancia_total": ganancia_total,
                        "nfts": nfts_con_ganancia,
                        "fecha": datetime.datetime.now()
                    }
                )
                
                return {
                    "ok": True,
                    "ganancia_total": ganancia_total,
                    "nfts": nfts_con_ganancia
                }
            else:
                return {
                    "ok": False,
                    "msg": "No tienes NFTs que generen ganancias"
                }
                
        except Exception as e:
            logger.error(f"Error en cálculo manual de ganancias para user_id={user_id}: {e}")
            return {"ok": False, "msg": "Error interno del sistema"}

# Instancia global del gestor
ganancias_manager = GananciasDiariasManager()

# Funciones de conveniencia
async def iniciar_ganancias_diarias():
    """Inicia el sistema de ganancias diarias"""
    await ganancias_manager.start()

async def detener_ganancias_diarias():
    """Detiene el sistema de ganancias diarias"""
    await ganancias_manager.stop()

async def calcular_ganancias_usuario(user_id: int) -> Dict:
    """Calcula ganancias manualmente para un usuario"""
    return await ganancias_manager.calcular_ganancias_manual(user_id) 