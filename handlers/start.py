from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from database.db import is_user_admin
from keyboards.inline_keyboards import get_main_menu_keyboard

WELCOME_TEXT = (
    "Добро пожаловать в наш бот!\n\n"
    "Я могу помочь вам с планированием вашего путешествия.\n"
    "Выберите интересующее вас действие:"
)

async def welcome(message: types.Message):
    """
    Отправляет пользователю приветственное сообщение с кнопками главного меню.
    Убирает любую reply‑клавиатуру.
    """
    await message.answer(
        WELCOME_TEXT,
        reply_markup=get_main_menu_keyboard(is_admin=is_user_admin(message.from_user.id))
    )

async def back_to_main_callback(source):
    """
    Возвращает пользователя в главное меню:
    - если source — CallbackQuery, редактирует текущее сообщение
    - если source — Message, отправляет новое
    """
    if isinstance(source, types.CallbackQuery):
        admin = is_user_admin(source.from_user.id)
        await source.message.edit_text(
            WELCOME_TEXT,
            reply_markup=get_main_menu_keyboard(is_admin=admin)
        )
        await source.answer()
    else:
        await welcome(source)
