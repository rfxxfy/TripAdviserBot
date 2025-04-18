from aiogram import types
from aiogram.fsm.context import FSMContext
from states.travel_states import TravelForm
from database.db import save_feedback
from handlers.start import back_to_main_callback
from keyboards.inline_keyboards import get_back_to_main_keyboard

async def feedback_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя текст обратной связи
    и предлагает вернуться в главное меню, если он передумает.
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
    Обрабатывает текст отзыва, сохраняет его и возвращает пользователя в главное меню.
    """
    try:
        save_feedback(message.from_user.id, message.text.strip())
        await message.answer("✅ Спасибо за ваш отзыв!")
    except Exception:
        await message.answer("❌ Произошла ошибка при сохранении отзыва. Попробуйте позже.")
    finally:
        await back_to_main_callback(message)
        await state.clear()