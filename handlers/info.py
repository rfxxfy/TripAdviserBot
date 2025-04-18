from aiogram import types
from database.db import is_user_admin
from keyboards.inline_keyboards import get_back_to_main_keyboard

async def bot_info(callback: types.CallbackQuery):
    """
    Выводит пользователю общую информацию о боте
    и показывает кнопку «Вернуться в главное меню».
    """
    await callback.message.edit_reply_markup(reply_markup=None)

    info_text = (
        "🤖 <b>JourneyPlannerBot</b> — интеллектуальный ассистент для путешественников!\n\n"
        "Бот помогает:\n"
        "• 📸 <b>Создавать маршруты с живописными местами</b>\n"
        "• 🍽️ <b>Планировать гастрономические маршруты</b>\n"
        "• 💰 <b>Оптимизировать траты</b>\n"
        "• 📆 <b>Распределять активности</b>\n\n"
        "<b>Как пользоваться:</b>\n"
        "1. Выберите тип маршрута\n"
        "2. Укажите локацию\n"
        "3. Задайте бюджет и другие параметры\n"
        "4. Получите готовый маршрут\n\n"
        "<i>Нажмите кнопку ниже, чтобы вернуться в главное меню.</i>"
    )

    await callback.message.answer(
        info_text,
        parse_mode="HTML",
        reply_markup=get_back_to_main_keyboard()
    )

    await callback.answer()