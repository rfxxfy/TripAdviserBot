"""
Этот модуль отвечает за выбор пользователем типов маршрутов,
переключение их состояния, подтверждение выбора и переход к уточнению параметров.
"""
from aiogram import types, F
from handlers import parameters
from handlers.start import welcome
from aiogram.fsm.context import FSMContext
from database.db import save_route_selection
from keyboards.inline_keyboards import get_route_types_keyboard

async def route_builder(callback: types.CallbackQuery, state: FSMContext):
    """
    Инициализирует выбор маршрутов, сохраняя их в FSM.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    
    await state.update_data(photo=False, budget=False, limited_time=False, food = False)

    routes_text = "Выберите типы маршрутов (можно выбрать несколько):"
    data = await state.get_data()
    await callback.message.answer(routes_text, reply_markup=get_route_types_keyboard(data))
    await callback.answer()

async def toggle_route_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Переключает состояние выбора маршрута (добавляет/убирает отметку).
    """
    route_type = callback.data.replace("toggle_", "")

    if route_type.startswith("photo_location"):
        await callback.answer()
        return  

    data = await state.get_data()

    if route_type in data:
        data[route_type] = not data[route_type]
        await state.update_data(**data)

    await callback.message.edit_reply_markup(reply_markup=get_route_types_keyboard(data))
    await callback.answer()

async def confirm_routes_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Подтверждение выбора маршрута и переход к сбору параметров.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    
    routes = await state.get_data()
    session_id = routes.get("session_id")
    selected_routes = []

    if routes.get("photo"):
        selected_routes.append("Маршрут с живописными местами")
        if session_id:
            save_route_selection(session_id, "photo", True)
    else:
        if session_id:
            save_route_selection(session_id, "photo", False)
            
    if routes.get("food"):
        selected_routes.append("Маршрут с питанием")
        if session_id:
            save_route_selection(session_id, "food", True)
    else:
        if session_id:
            save_route_selection(session_id, "food", False)

    if not selected_routes:
        await callback.message.answer(
            "Вы не выбрали ни одного маршрута. Пожалуйста, выберите хотя бы один маршрут.",
            reply_markup=get_route_types_keyboard(routes)
        )
        await callback.answer()
        return

    response_text = "Вы выбрали следующие маршруты:\n" + "\n".join(f"- <b><u>{r}</u></b>" for r in selected_routes)
    response_text += "\n\nПереходим к уточнению параметров."

    await callback.message.answer(response_text, parse_mode="HTML")
    await callback.answer()

    await state.update_data(selected_routes=routes)
    await parameters.start_parameter_collection(callback, routes, state)

async def back_to_main_callback(callback: types.CallbackQuery):
    """
    Возвращает пользователя в главное меню.

    :param callback: Callback-запрос от нажатой кнопки.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    await welcome(callback.message)
    await callback.answer()
