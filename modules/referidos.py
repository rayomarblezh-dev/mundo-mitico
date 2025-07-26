from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.database import (
    contar_referidos,
    contar_referidos_activos
)

async def referidos_handler(event):
    """Handler de referidos (funciona con mensajes y callbacks)"""
    # Determinar si es un mensaje o callback
    if hasattr(event, 'from_user'):
        user_id = event.from_user.id
        is_callback = hasattr(event, 'data')
    else:
        return
    
    bot_username = (await event.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    # Obtener progreso de referidos
    total = await contar_referidos(user_id)
    activos = await contar_referidos_activos(user_id)

    mensaje = (
        "👥 Referidos\n\n"
        "Invita a tus amigos y obtén recompensas exclusivas por cada uno que se una y participe.\n\n"
        "Recompensas:\n"
        "• Por cada 10 invitaciones: 1 Hada\n"
        "• Por cada referido que invierta: 1 Elfo\n\n"
        "Tu progreso:\n"
        f"• Referidos totales: {total}\n"
        f"• Referidos activos: {activos}\n\n"
        "¡Sigue invitando para obtener más recompensas!"
    )

    share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Compartir",
                url=f"https://t.me/share/url?url={ref_link}"
            )
        ],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="start_volver")]
    ])

    # Enviar mensaje según el tipo de evento
    if is_callback:
        try:
            await event.message.edit_text(mensaje, parse_mode="HTML", reply_markup=share_keyboard)
        except Exception as e:
            if "message is not modified" in str(e):
                # El mensaje es el mismo, solo responder al callback
                pass
            else:
                # Otro error, intentar enviar nuevo mensaje
                await event.message.answer(mensaje, parse_mode="HTML", reply_markup=share_keyboard)
        await event.answer()
    else:
        await event.answer(mensaje, parse_mode="HTML", reply_markup=share_keyboard)