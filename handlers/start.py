from aiogram import types
from keyboards.inline_keyboards import get_main_menu_keyboard

async def welcome(message: types.Message):
    """
    Отправляет пользователю приветственное сообщение с кнопками главного меню.
    """
    welcome_text = """Добро пожаловать в наш бот!

Я могу помочь вам с планированием вашего путешествия.
Выберите интересующее вас действие:"""
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())

