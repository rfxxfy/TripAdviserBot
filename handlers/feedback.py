from aiogram import types
from keyboards.inline_keyboards import get_back_to_main_keyboard

async def feedback_handler(callback: types.CallbackQuery):
    """
    Обрабатывает запрос на отправку отзыва через Google Forms.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    
    await callback.message.answer(
        "Спасибо за желание оставить отзыв! Пожалуйста, заполните нашу форму по ссылке: ссылка",
        reply_markup=get_back_to_main_keyboard()
    )
    await callback.answer()