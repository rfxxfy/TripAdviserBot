import asyncio

import openai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from rag import RAGService

with open("tokens/token.txt", "r", encoding="utf-8") as f:
    TELEGRAM_BOT_TOKEN = f.read().strip()

with open("tokens/ai_token.txt", "r", encoding="utf-8") as f:
    OPENAI_API_KEY = f.read().strip()

openai.api_key = OPENAI_API_KEY

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
rag_service = RAGService()


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply(
        "Привет! Отправь мне свою геопозицию (📍) или напиши название города, "
        "и я найду ближайшие музеи, парки и кафе."
    )


@dp.message(lambda msg: msg.location is not None)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    preferences = ["музеи", "парки", "кафе"]

    text = rag_service.retrieve_documents(
        location_name="",
        preferences=preferences,
        lat=lat,
        lon=lon
    )
    await message.reply(text)


@dp.message()
async def handle_text(message: types.Message):
    user_text = message.text.strip()
    preferences = ["музеи", "парки", "кафе"]

    text = rag_service.retrieve_documents(
        location_name=user_text,
        preferences=preferences,
        lat=None,
        lon=None
    )
    await message.reply(text)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())