from aiogram import types
from aiogram.fsm.context import FSMContext
from states.travel_states import TravelForm
from keyboards.inline_keyboards import get_back_to_main_keyboard
from handlers.start import welcome
from database.db import save_feedback

async def feedback_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя текст обратной связи.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    
    await callback.message.answer(
        "📝 Пожалуйста, напишите ваш отзыв или предложение. Мы очень ценим ваше мнение!",
        reply_markup=get_back_to_main_keyboard()
    )
    
    await state.set_state(TravelForm.waiting_for_feedback)
    await callback.answer()

async def process_feedback(message: types.Message, state: FSMContext):
    """
    Обрабатывает полученный текст обратной связи.
    """
    feedback_text = message.text.strip()
    
    user_id = message.from_user.id
    try:
        feedback_id = save_feedback(user_id, feedback_text)
        await message.answer("✅ Спасибо за ваш отзыв! Мы обязательно учтем ваше мнение.")
        await welcome(message)
    except Exception as e:
        print(f"Ошибка при сохранении отзыва: {e}")
        await message.answer("❌ Произошла ошибка при сохранении отзыва. Попробуйте позже.")
        await welcome(message)
        
    await state.clear()