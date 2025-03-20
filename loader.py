"""
loader.py – Инициализация бота и диспетчера.

Этот файл создает объекты:
- bot: экземпляр Telegram-бота с токеном из config.py.
- dp: диспетчер для обработки сообщений и callback-запросов.
- storage: хранилище состояний FSM (по умолчанию MemoryStorage).

Используется для централизованного импорта bot и dp в другие модули.
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from rag import RAGService

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)
rag_service = RAGService()
