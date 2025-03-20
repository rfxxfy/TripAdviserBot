from aiogram.types import BotCommand
from loader import bot

async def set_bot_commands():
    """
    Создает подсказки для основных команд бота
    """
    commands = [
        BotCommand(command="/start", description="Начать работу бота")
    ]
    await bot.set_my_commands(commands)
