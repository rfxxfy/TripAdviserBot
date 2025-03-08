import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def welcome(message: types.Message):
    welcome_text = """Добро пожаловать в наш бот!

Я могу помочь вам с планированием вашего путешествия.
Выберите интересующее вас действие:"""

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Построить маршрут")],
            [KeyboardButton(text="Найти ближайшие обменники валюты с выгодным курсом")],
            [KeyboardButton(text="Информация про бота")]
        ],
        resize_keyboard=True
    )
    
    await message.reply(welcome_text, reply_markup=keyboard)

dp.message.register(welcome, Command("start"))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())