from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.database import (
    contar_referidos,
    contar_referidos_activos
)

async def referidos_handler(message: types.Message):
    user_id = message.from_user.id
    bot_username = (await message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    # Obtener progreso de referidos
    total = await contar_referidos(user_id)
    activos = await contar_referidos_activos(user_id)

    mensaje = (
        f"<b>👥 Referidos</b>\n"
        f"<blockquote expandable>Invita a tus amigos y obtén recompensas exclusivas por cada uno que se una y participe.</blockquote>\n\n"
        f"🎁 <b>Recompensas:</b>\n"
        f"• Por cada 10 invitaciones: <b>1 Hada</b>\n"
        f"• Por cada referido que invierta: <b>1 Elfo</b>\n\n"
        f"📊 <b>Tu progreso:</b>\n"
        f"• Referidos totales: <b>{total}</b>\n"
        f"• Referidos activos: <b>{activos}</b>\n\n"
        f"¡Sigue invitando para obtener más recompensas!"
    )

    share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Compartir",
                url=f"https://t.me/share/url?url={ref_link}"
            )
        ]
    ])

    await message.answer(mensaje, parse_mode="HTML", reply_markup=share_keyboard)