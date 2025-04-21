from aiogram import types
from helpers.blacklist import add_to_blacklist

async def report_poi(callback_query: types.CallbackQuery):
    """
    Пользователь пожаловался, что место неверно.
    callback_data = report_poi:<poi_name>
    """
    _, raw_name = callback_query.data.split(":", 1)
    poi_name = raw_name.replace('_',' ').strip().lower()
    add_to_blacklist(poi_name)
    await callback_query.answer("Спасибо! Мы исключим это место из будущих маршрутов.", show_alert=True)