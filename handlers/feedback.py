from aiogram import types
from keyboards.inline_keyboards import get_back_to_main_keyboard

async def feedback_handler(callback: types.CallbackQuery):
    """
    Обрабатывает запрос на отправку отзыва или предложения от пользователя.
    """
    await callback.message.answer(
        "Пожалуйста, напишите свой отзыв или предложение:",
        reply_markup=get_back_to_main_keyboard()
    )
    await callback.answer()