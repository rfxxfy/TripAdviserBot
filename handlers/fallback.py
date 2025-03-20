from aiogram import types
from aiogram.fsm.context import FSMContext

# Универсальный fallback-хендлер для входящих сообщений
async def fallback_message_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        await message.answer("Сейчас бот не ожидает сообщений. Воспользуйтесь командами или кнопками меню.")

