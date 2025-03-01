import asyncio
from aiogram import Bot, Dispatcher, types

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.reply("Hello!")

async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
