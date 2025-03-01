import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def welcome(message: types.Message):
    await message.reply("Залупа")

dp.message.register(welcome, Command("start"))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
