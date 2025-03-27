from aiogram import BaseMiddleware
from typing import Any, Dict, Callable, Awaitable
from aiogram.types import Message, CallbackQuery
from database.db import register_user, start_session

class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware для автоматического сохранения данных о пользователях
    и их взаимодействиях с ботом в базу данных.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user = event.from_user
        
        user_id = register_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if isinstance(event, Message) and event.text == "/start" or \
           isinstance(event, CallbackQuery) and event.data == "back_to_main":
            session_id = start_session(user_id)
            data["session_id"] = session_id
            
            if isinstance(event, CallbackQuery) and hasattr(event, 'message'):
                state = data.get('state')
                if state:
                    await state.update_data(session_id=session_id)
        
        return await handler(event, data)