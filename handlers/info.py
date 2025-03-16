from aiogram import types
from keyboards.inline_keyboards import get_back_to_main_keyboard

async def bot_info(callback: types.CallbackQuery):
    """
    Выводит пользователю общую информацию о боте.
    """
    await callback.message.answer(
        "Этот бот поможет вам спланировать путешествие, построить маршруты и найти выгодные обменники валюты.",
        reply_markup=get_back_to_main_keyboard()
    )
    await callback.answer()
