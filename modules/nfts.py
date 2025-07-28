import logging
import os
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import (
    usuario_tiene_nft_comun, 
    usuario_tiene_nft_ghost, 
    procesar_compra_item,
    obtener_balance_usuario
)
from modules.constants import NFTS_CONFIG, obtener_imagen_nft_para_telegram, verificar_imagen_nft_existe

logger = logging.getLogger(__name__)

# Configuración de NFTs (usando configuración centralizada)

async def nfts_handler(callback: types.CallbackQuery):
    """Handler para mostrar la sección de NFTs"""
    user_id = callback.from_user.id
    
    try:
        balance = await obtener_balance_usuario(user_id)
        
        mensaje = (
            "<b>🎨 NFTs</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Colecciones únicas y limitadas de arte digital con poderes especiales.</b>\n\n"
            f"<b>💰 Balance:</b> <code>{balance:.3f} TON</code>\n\n"
            "<b>Características de los NFTs:</b>\n"
            "  • 💸 Generan ganancias diarias en TON\n"
            "  • ⏳ Duración limitada de 30 días\n"
            "  • 🦄 Rareza única - Solo puedes tener 1 de cada tipo\n\n"
            "<b>Restricciones:</b>\n"
            "  • Solo 1 NFT común (Moguri o Gárgola)\n"
            "  • Solo 1 NFT Ghost\n\n"
            "<b>💡 Consejo:</b> Los NFTs son la mejor inversión para generar TON pasivamente."
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💀 Moguri-NFT", callback_data="nft_moguri")
        builder.button(text="🦇 Gargola-NFT", callback_data="nft_gargola")
        builder.button(text="👻 Ghost-NFT", callback_data="nft_ghost")
        builder.button(text="🔙 Volver", callback_data="tienda_volver")
        builder.adjust(2, 1, 1)
        keyboard = builder.as_markup()
        
        try:
            await callback.message.delete()
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=keyboard)
        except Exception:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en nfts_handler para user_id={user_id}: {e}")
        await callback.answer("<b>❌ Error al cargar NFTs.</b>", show_alert=True)
    
    await callback.answer()

async def mostrar_nft_detallado(callback: types.CallbackQuery, nft_key: str):
    """Muestra información detallada de un NFT específico"""
    user_id = callback.from_user.id
    
    try:
        nft_config = NFTS_CONFIG.get(nft_key)
        if not nft_config:
            await callback.answer("<b>❌ NFT no encontrado.</b>", show_alert=True)
            return
        
        balance = await obtener_balance_usuario(user_id)
        
        # Verificar si el usuario ya tiene este tipo de NFT
        tiene_nft = False
        if nft_key in ["moguri", "gargola"]:
            tiene_nft = await usuario_tiene_nft_comun(user_id)
        elif nft_key == "ghost":
            tiene_nft = await usuario_tiene_nft_ghost(user_id)
        
        # Calcular ROI
        ganancia_total = nft_config["ganancia_diaria"] * nft_config["duracion"]
        roi_porcentaje = ((ganancia_total - nft_config["precio"]) / nft_config["precio"]) * 100
        
        mensaje = (
            f"<b>{nft_config['emoji']} {nft_config['nombre']} ({nft_config['rareza']})</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>{nft_config['descripcion']}</b>\n\n"
            f"<b>Información de Inversión:</b>\n"
            f"  • <b>Precio:</b> {nft_config['precio']} TON\n"
            f"  • <b>Ganancia diaria:</b> {nft_config['ganancia_diaria']} TON\n"
            f"  • <b>Duración:</b> {nft_config['duracion']} días\n"
            f"  • <b>Ganancia total:</b> {ganancia_total} TON\n"
            f"  • <b>ROI:</b> {roi_porcentaje:.1f}%\n\n"
            f"<b>Características:</b>\n"
            f"  • NFT de rareza {nft_config['rareza'].lower()}\n"
            f"  • Generación automática de ganancias\n"
            f"  • Duración de {nft_config['duracion']} días\n\n"
            f"<b>Tu balance:</b> <code>{balance:.3f} TON</code>"
        )
        
        if tiene_nft:
            mensaje += "\n\n⚠️ <b>Ya tienes un NFT de este tipo</b>"
            builder = InlineKeyboardBuilder()
            builder.button(text="🔙 Volver", callback_data="tienda_nfts")
            keyboard = builder.as_markup()
        else:
            builder = InlineKeyboardBuilder()
            builder.button(text=f"💎 Comprar", callback_data=f"comprar_nft_{nft_key}")
            builder.button(text="🔙 Volver", callback_data="tienda_nfts")
            keyboard = builder.as_markup()
        
        # Intentar enviar imagen si existe usando la función centralizada
        photo = obtener_imagen_nft_para_telegram(nft_key)
        if photo:
            try:
                await callback.message.delete()
                await callback.message.answer_photo(
                    photo, 
                    caption=mensaje, 
                    parse_mode="HTML", 
                    reply_markup=keyboard
                )
            except Exception:
                await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
        else:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error en mostrar_nft_detallado para user_id={user_id}, nft={nft_key}: {e}")
        await callback.answer("<b>❌ Error al mostrar NFT.</b>", show_alert=True)
    
    await callback.answer()

async def nft_moguri_handler(callback: types.CallbackQuery):
    """Handler para el NFT Moguri"""
    await mostrar_nft_detallado(callback, "moguri")

async def nft_gargola_handler(callback: types.CallbackQuery):
    """Handler para el NFT Gargola"""
    await mostrar_nft_detallado(callback, "gargola")

async def nft_ghost_handler(callback: types.CallbackQuery):
    """Handler para el NFT Ghost"""
    await mostrar_nft_detallado(callback, "ghost")

async def volver_nfts_handler(callback: types.CallbackQuery):
    """Handler para volver al menú principal de NFTs"""
    await nfts_handler(callback)

async def comprar_nft_handler(callback: types.CallbackQuery, nft_key: str):
    """Handler genérico para comprar NFTs"""
    user_id = callback.from_user.id
    
    try:
        nft_config = NFTS_CONFIG.get(nft_key)
        if not nft_config:
            await callback.answer("<b>❌ NFT no encontrado.</b>", show_alert=True)
            return
        
        # Verificar si ya tiene el NFT
        tiene_nft = False
        if nft_key in ["moguri", "gargola"]:
            tiene_nft = await usuario_tiene_nft_comun(user_id)
        elif nft_key == "ghost":
            tiene_nft = await usuario_tiene_nft_ghost(user_id)
        
        if tiene_nft:
            await callback.answer("<b>❌ Ya tienes un NFT de este tipo.</b>", show_alert=True)
            return
        
        # Procesar compra
        item = {
            "tipo": "nft",
            "nombre": nft_config["nombre"],
            "precio": nft_config["precio"]
        }
        
        resultado = await procesar_compra_item(user_id, item)
        
        if resultado.get("ok"):
            ganancia_total = nft_config["ganancia_diaria"] * nft_config["duracion"]
            roi_porcentaje = ((ganancia_total - nft_config["precio"]) / nft_config["precio"]) * 100
            
            mensaje = (
                "<b>✅ ¡COMPRA EXITOSA!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>🎉 ¡Has adquirido el {nft_config['emoji']} {nft_config['nombre']}!</b>\n\n"
                f"<b>Información de tu inversión:</b>\n"
                f"  • <b>Precio pagado:</b> {nft_config['precio']} TON\n"
                f"  • <b>Ganancia diaria:</b> {nft_config['ganancia_diaria']} TON\n"
                f"  • <b>Duración:</b> {nft_config['duracion']} días\n"
                f"  • <b>Ganancia total:</b> {ganancia_total} TON\n"
                f"  • <b>ROI:</b> {roi_porcentaje:.1f}%\n\n"
                f"<b>Tu NFT comenzará a generar ganancias automáticamente desde hoy.</b>\n"
                f"<b>¡Disfruta de tus ganancias diarias!</b>"
            )
        else:
            mensaje = (
                "<b>❌ Error en la Compra</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>{resultado.get('msg', 'Ha ocurrido un error inesperado.')}</b>\n\n"
                "<b>Posibles causas:</b>\n"
                "  • Balance insuficiente\n"
                "  • Ya tienes un NFT de este tipo\n"
                "  • Error en el sistema"
            )
        
        volver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="tienda_nfts")],
            [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="start_volver")]
        ])
        
        try:
            await callback.message.delete()
            await callback.message.answer(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
        except Exception:
            await callback.message.edit_text(mensaje, parse_mode="HTML", reply_markup=volver_keyboard)
            
    except Exception as e:
        logger.error(f"Error en comprar_nft_handler para user_id={user_id}, nft={nft_key}: {e}")
        await callback.answer("<b>❌ Error al procesar la compra.</b>", show_alert=True)
    
    await callback.answer()

async def comprar_nft_moguri_handler(callback: types.CallbackQuery):
    """Handler para comprar NFT Moguri"""
    await comprar_nft_handler(callback, "moguri")

async def comprar_nft_gargola_handler(callback: types.CallbackQuery):
    """Handler para comprar NFT Gargola"""
    await comprar_nft_handler(callback, "gargola")

async def comprar_nft_ghost_handler(callback: types.CallbackQuery):
    """Handler para comprar NFT Ghost"""
    await comprar_nft_handler(callback, "ghost")

def register_nfts_handlers(dp):
    """Registra todos los handlers del módulo NFTs"""
    # Callbacks principales
    dp.callback_query.register(nft_moguri_handler, lambda c: c.data == "nft_moguri")
    dp.callback_query.register(nft_gargola_handler, lambda c: c.data == "nft_gargola")
    dp.callback_query.register(nft_ghost_handler, lambda c: c.data == "nft_ghost")
    dp.callback_query.register(volver_nfts_handler, lambda c: c.data == "tienda_nfts")
    
    # Callbacks de compra
    dp.callback_query.register(comprar_nft_moguri_handler, lambda c: c.data == "comprar_nft_moguri")
    dp.callback_query.register(comprar_nft_gargola_handler, lambda c: c.data == "comprar_nft_gargola")
    dp.callback_query.register(comprar_nft_ghost_handler, lambda c: c.data == "comprar_nft_ghost") 