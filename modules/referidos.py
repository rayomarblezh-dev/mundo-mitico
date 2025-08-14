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
        "<b>👥 Referrals</b>\n\n"
        "<b>Invite your friends and get exclusive rewards for each one who joins and participates.</b>\n\n"
        "<b>🎁 Rewards:</b>\n"
        "  • For every 10 invitations: <b>1 Fairy 🧚‍♀️</b>\n"
        "  • For each referral who invests: <b>1 Elf 🧝‍♀️</b>\n\n"
        "<b>📊 Your progress:</b>\n"
        f"  • Total referrals: <b>{total}</b>\n"
        f"  • Active referrals: <b>{activos}</b>\n\n"
        "<b>💡 Tip:</b> Keep inviting to get more rewards!"
    )

    share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Share Link",
                url=f"https://t.me/share/url?url={ref_link}"
            )
        ],
        [InlineKeyboardButton(text="« Back", callback_data="perfil")]
    ])

    # Enviar mensaje según el tipo de evento
    if is_callback:
        try:
            await event.message.edit_text(mensaje, parse_mode="HTML", reply_markup=share_keyboard)
        except Exception as e:
            if "message is not modified" in str(e):
                pass
            else:
                await event.message.answer(mensaje, parse_mode="HTML", reply_markup=share_keyboard)
        await event.answer()
    else:
        await event.answer(mensaje, parse_mode="HTML", reply_markup=share_keyboard)