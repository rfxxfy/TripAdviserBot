import re
from helpers.validators import is_valid_coordinate
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from loader import rag_service
from states.travel_states import TravelForm
from keyboards.inline_keyboards import (
    PHOTO_OPTIONS, CUISINE_OPTIONS,
    get_photo_locations_keyboard,
    get_cuisine_keyboard,
    get_first_time_keyboard
)
from database.db import (
    start_session, save_location, save_photo_location,
    save_cuisine, save_route_parameters, complete_session
)
from LLM.llm import generate_route

async def start_parameter_collection(
    callback: types.CallbackQuery,
    selected_routes: dict,
    state: FSMContext
):
    data = await state.get_data()
    session_id = data.get("session_id")
    if not session_id:
        session_id = start_session(callback.from_user.id)
        await state.update_data(session_id=session_id)

    questions = ["location", "budget", "days", "first_time"]
    if selected_routes.get("photo"):
        questions.append("photo")
    if selected_routes.get("food"):
        questions.append("food")

    await state.update_data(
        selected_routes=selected_routes,
        questions_order=questions,
        question_index=0
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    msg = await callback.message.answer(
        "📍 Пожалуйста, отправьте свою геолокацию или введите адрес отправления",
        reply_markup=kb
    )
    await state.update_data(last_message_with_keyboard_id=msg.message_id)
    await state.set_state(TravelForm.waiting_for_location)
    await callback.answer()


async def ask_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order = data.get("questions_order", [])
    idx = data.get("question_index", 0)

    last_id = data.get("last_message_with_keyboard_id")
    if last_id:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=last_id,
                reply_markup=None
            )
        except TelegramBadRequest:
            pass

    if idx >= len(order):
        await finish_parameters_collection(message, state)
        return

    step = order[idx]
    if step == "budget":
        await message.answer(
            "💰 Введите ваш бюджет в рублях:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(TravelForm.waiting_for_budget)

    elif step == "photo":
        await message.answer(
            "📸 Выберите интересующие фото‑локации:",
            reply_markup=get_photo_locations_keyboard([], PHOTO_OPTIONS)
        )
        await state.set_state(TravelForm.waiting_for_photo_locations)

    elif step == "food":
        await message.answer(
            "🍽️ Выберите предпочитаемые кухни:",
            reply_markup=get_cuisine_keyboard([], CUISINE_OPTIONS)
        )
        await state.set_state(TravelForm.waiting_for_cuisine)

    elif step == "days":
        await message.answer("📆 Сколько дней вы планируете путешествовать?")
        await state.set_state(TravelForm.waiting_for_days)

    elif step == "first_time":
        await message.answer(
            "🏙️ Вы впервые посещаете этот город?",
            reply_markup=get_first_time_keyboard()
        )
        await state.set_state(TravelForm.waiting_for_first_time)

    else:
        await finish_parameters_collection(message, state)


async def process_location(message: types.Message, state: FSMContext):
    """
    Принимаем локацию или текст. Здесь НЕ отправляем отдельное сообщение,
    remove-клавиатуру уберёт следующая функция ask_next_question.
    """
    data = await state.get_data()
    session_id = data.get("session_id")

    if message.location:
        lat, lon = message.location.latitude, message.location.longitude
        loc = f"{lat}, {lon}"
        await state.update_data(location=loc)
        save_location(session_id, "Координаты", lat, lon)
    else:
        text = message.text.strip()
        if is_valid_coordinate(text):
            lat, lon = re.split(r'[,\s]+', text)
            loc = (float(lat), float(lon))
            await state.update_data(location=loc)
            save_location(session_id, text, lat, lon)
        else:
            cords = rag_service.get_coordinates(text)
            if not cords:
                await message.answer(
                    "🚨 Не удалось найти место. Попробуйте точнее или отправьте геолокацию."
                )
                return
            await state.update_data(location=text, coords=cords)
            save_location(session_id, text, cords[0], cords[1])

    await state.update_data(question_index=data.get("question_index", 0) + 1)
    await ask_next_question(message, state)

async def process_budget(message: types.Message, state: FSMContext):
    try:
        b = float(message.text)
        if b < 0:
            raise ValueError
        if b > 1e6:
            b = 1e6
    except ValueError:
        await message.answer("🚨 Введите корректное число для бюджета.")
        return

    await state.update_data(budget=b)
    data = await state.get_data()
    await state.update_data(question_index=data.get("question_index", 0) + 1)
    await ask_next_question(message, state)


async def toggle_photo_locations(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sel = data.get("photo_locations", [])
    _, opt = callback.data.split(":", 1)
    if opt == "all":
        sel = [] if len(sel) == len(PHOTO_OPTIONS) else PHOTO_OPTIONS.copy()
    else:
        if opt in sel:
            sel.remove(opt)
        else:
            sel.append(opt)
    await state.update_data(photo_locations=sel)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_photo_locations_keyboard(sel, PHOTO_OPTIONS)
        )
    except TelegramBadRequest:
        pass
    await callback.answer("Обновлено!")


async def confirm_photo_locations(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    for loc in data.get("photo_locations", []):
        save_photo_location(data.get("session_id"), loc)
    await callback.answer("Фото‑локации сохранены!")
    await state.update_data(question_index=data.get("question_index", 0) + 1)
    await ask_next_question(callback.message, state)


async def toggle_cuisine(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sel = data.get("cuisine_options", [])
    _, opt = callback.data.split(":", 1)
    if opt == "all":
        sel = [] if len(sel) == len(CUISINE_OPTIONS) else CUISINE_OPTIONS.copy()
    else:
        if opt in sel:
            sel.remove(opt)
        else:
            sel.append(opt)
    await state.update_data(cuisine_options=sel)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_cuisine_keyboard(sel, CUISINE_OPTIONS)
        )
    except TelegramBadRequest:
        pass
    await callback.answer("Обновлено!")


async def confirm_cuisine(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    for c in data.get("cuisine_options", []):
        save_cuisine(data.get("session_id"), c)
    await callback.answer("Кухни сохранены!")
    await state.update_data(question_index=data.get("question_index", 0) + 1)
    await ask_next_question(callback.message, state)


async def process_days(message: types.Message, state: FSMContext):
    try:
        d = int(message.text)
        if not (1 <= d <= 7):
            raise ValueError
    except ValueError:
        await message.answer("🚨 Введите число от 1 до 7 для дней.")
        return
    await state.update_data(days=d)
    data = await state.get_data()
    await state.update_data(question_index=data.get("question_index", 0) + 1)
    await ask_next_question(message, state)


async def process_first_time(callback: types.CallbackQuery, state: FSMContext):
    _, ans = callback.data.split(":", 1)
    await state.update_data(is_first_time=(ans == "yes"))
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Спасибо!")
    data = await state.get_data()
    await state.update_data(question_index=data.get("question_index", 0) + 1)
    await ask_next_question(callback.message, state)


async def finish_parameters_collection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    session_id = data.get("session_id")
    save_route_parameters(session_id, data.get("budget"), data.get("days"))
    complete_session(session_id)

    resp = (
        "✅ Сбор параметров завершён!\n\n"
        f"📍 Локация: {data.get('location')}\n"
        f"💰 Бюджет: {data.get('budget')} руб.\n"
        f"📆 Дней: {data.get('days')}\n"
    )
    if data["selected_routes"].get("photo"):
        resp += f"📸 Локации: {', '.join(data.get('photo_locations', []))}\n"
    if data["selected_routes"].get("food"):
        resp += f"🍽️ Кухни: {', '.join(data.get('cuisine_options', []))}\n"
    resp += "\nОжидайте выполнения запроса ⏳"

    await message.answer(resp)

    llm = generate_route(
        departure=str(data.get("location")),
        preferences=data.get("photo_locations", []) + data.get("cuisine_options", []),
        route_type=" и ".join([
            t for t in (
                "живописными местами" if data["selected_routes"].get("photo") else "",
                "питанием" if data["selected_routes"].get("food") else ""
            ) if t
        ]),
        days=int(data.get("days")),
        budget=float(data.get("budget")),
        is_first_time=data.get("is_first_time", True)
    )
    await message.answer(llm, parse_mode="HTML")
    await state.clear()
