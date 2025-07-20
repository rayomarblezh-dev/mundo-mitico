from aiogram import types

async def tutorials_callback_handler(callback: types.CallbackQuery):
    cartel = (
        "⚠️ Próximamente\n\n"
    )
    await callback.answer(cartel, show_alert=True)
