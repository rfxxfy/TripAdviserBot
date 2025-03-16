from aiogram import types
from keyboards.inline_keyboards import get_back_to_main_keyboard

async def currency_exchange(callback: types.CallbackQuery):
    """
    Обрабатывает запрос на поиск обменников валюты.
    """
    await callback.message.answer("Функция поиска обменников валюты в разработке.", reply_markup=get_back_to_main_keyboard())
    await callback.answer()