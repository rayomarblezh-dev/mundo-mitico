from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.database import (
    agregar_referido,
    obtener_referidos,
    contar_referidos,
    contar_referidos_activos
)

async def referidos_handler(message: types.Message):
    user_id = message.from_user.id
    ref_link = f"https://t.me/{(await message.bot.get_me()).username}?start=ref_{user_id}"

    # Obtener progreso de referidos
    total = await contar_referidos(user_id)
    activos = await contar_referidos_activos(user_id)
    hadas = total // 10
    elfos = activos  # 1 elfo por cada referido activo (primer depósito)

    mensaje = (
        f"<i><b>👥 Referidos</b>\n\n"
        f"— Invita a tus amigos y gana recompensas exclusivas.\n\n"
        f"— Comparte tu enlace único y ambos recibirán beneficios especiales.\n\n"
        f"<b>🎁 Recompensas:</b>\n\n"
        f"— Cada 10 invitaciones: 1 Hada\n"
        f"— Cada referido que invierta: 1 Elfo\n\n"
        f"<b>Progreso:</b>\n"
        f"• Referidos totales: <b>{total}</b>\n"
        f"• Referidos activos: <b>{activos}</b>\n"
        f"• Hadas obtenidas: <b>{hadas}</b>\n"
        f"• Elfos obtenidos: <b>{elfos}</b>\n\n"
        f"<b>¡Más invitados, más recompensas!</b></i>"
    )
    share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Compartir", url=f"https://t.me/share/url?url={ref_link}")],
    ])
    await message.answer(mensaje, parse_mode="HTML", reply_markup=share_keyboard)