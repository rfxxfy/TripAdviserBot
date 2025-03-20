"""
Обработчики для сбора параметров пользователя.
"""

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from states.travel_states import TravelForm
from keyboards.inline_keyboards import get_photo_locations_keyboard, get_back_to_main_keyboard, PHOTO_OPTIONS

async def start_parameter_collection(
        callback: types.CallbackQuery,
        selected_routes: dict,
        state: FSMContext):
    """
    Сохраняет выбранные маршруты и формирует порядок вопросов.
    Затем запрашивает у пользователя геопозицию/адрес отправления.
    """
    questions_order = ["location", "budget", "days"]
    if selected_routes.get("photo"):
        questions_order.append("photo")

    await state.update_data(
        selected_routes=selected_routes,
        questions_order=questions_order,
        question_index=0
    )

    message = await callback.message.answer(
        "📍 Пожалуйста, отправьте свою геопозицию или введите адрес отправления.",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.update_data(last_message_with_keyboard_id=message.message_id)
    await state.set_state(TravelForm.waiting_for_location)
    await callback.answer()


async def ask_next_question(message: types.Message, state: FSMContext):
    """
    Задает следующий вопрос пользователю на основе сохраненного порядка вопросов.
    """
    data = await state.get_data()
    questions_order = data.get("questions_order", [])
    index = data.get("question_index", 0)

    last_keyboard_id = data.get("last_message_with_keyboard_id")
    if last_keyboard_id:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=last_keyboard_id,
                reply_markup=None
            )
        except Exception:
            pass

    if index >= len(questions_order):
        await finish_parameters_collection(message, state)
        return

    next_question = questions_order[index]
    if next_question == "budget":
        await message.answer("💰 Введите ваш бюджет в рублях:")
        await state.set_state(TravelForm.waiting_for_budget)
    elif next_question == "photo":
        await message.answer(
            "📸 Выберите интересующие фото‑локации:",
            reply_markup=get_photo_locations_keyboard([], PHOTO_OPTIONS)
        )
        await state.set_state(TravelForm.waiting_for_photo_locations)
    elif next_question == "days":
        await message.answer("📆 Сколько дней вы планируете путешествовать?")
        await state.set_state(TravelForm.waiting_for_days)
    else:
        await finish_parameters_collection(message, state)


async def process_location(message: types.Message, state: FSMContext):
    """
    Сохраняет геопозицию, переданную в виде текста или координат,
    и переходит к следующему вопросу.
    Обработка происходит только если бот ожидает геопозицию.
    """
    current_state = await state.get_state()
    if current_state != TravelForm.waiting_for_location:
        return

    if message.location:
        location = f"{message.location.latitude}, {message.location.longitude}"
    else:
        location = message.text

    await state.update_data(location=location)
    data = await state.get_data()
    question_index = data.get("question_index", 0) + 1
    await state.update_data(question_index=question_index)
    await ask_next_question(message, state)


async def process_budget(message: types.Message, state: FSMContext):
    """
    Сохраняет введенный бюджет и переходит к следующему вопросу.
    """
    try:
        budget = float(message.text)
    except ValueError:
        await message.answer("🚨 Введите корректное число для бюджета.")
        return
    await state.update_data(budget=budget)
    data = await state.get_data()
    question_index = data.get("question_index", 0) + 1
    await state.update_data(question_index=question_index)
    await ask_next_question(message, state)


async def toggle_photo_locations(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает изменение выбора фото‑локаций.
    """
    data = await state.get_data()
    selected = data.get("photo_locations", [])
    if ":" not in callback.data:
        await callback.answer("Ошибка в callback data")
        return
    action, option = callback.data.split(":", 1)
    if action != "toggle_photo_location":
        await callback.answer("Ошибка в обработке callback.")
        return

    if option in selected:
        selected.remove(option)
    else:
        selected.append(option)

    await state.update_data(photo_locations=selected)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_photo_locations_keyboard(selected, PHOTO_OPTIONS)
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise

    await callback.answer("Обновлено!")


async def confirm_photo_locations(callback: types.CallbackQuery, state: FSMContext):
    """
    Завершает этап выбора фото‑локаций и переходит к следующему вопросу.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    question_index = data.get("question_index", 0) + 1
    await state.update_data(question_index=question_index)
    await callback.answer("Выбор фото‑локаций подтверждён!")
    await ask_next_question(callback.message, state)


async def process_days(message: types.Message, state: FSMContext):
    """
    Сохраняет введенное количество дней и переходит к завершению сбора параметров.
    """
    try:
        days = int(message.text)
    except ValueError:
        await message.answer("🚨 Введите корректное число для количества дней.")
        return
    await state.update_data(days=days)
    data = await state.get_data()
    question_index = data.get("question_index", 0) + 1
    await state.update_data(question_index=question_index)
    await ask_next_question(message, state)


async def finish_parameters_collection(message: types.Message, state: FSMContext):
    """
    Завершает сбор параметров:
    1. Выводит собранные данные.
    2. Вызывает RAG-сервис для поиска POI по полученной геопозиции.
    3. Отправляет результаты пользователю.
    4. Очищает состояние FSM.
    """
    data = await state.get_data()
    selected_routes = data.get("selected_routes", {})
    location = data.get("location", "не указана")
    budget = data.get("budget", "не указан")
    photo_locations = data.get("photo_locations", [])
    days = data.get("days", "не указано")

    response = "✅ Сбор параметров завершён!\n\n"
    response += f"📍 **Локация**: {location}\n"
    response += f"💰 **Бюджет**: {budget} руб.\n"
    response += f"📆 **Дней**: {days}\n"
    if selected_routes.get("photo"):
        response += f"📸 **Фото‑локации**: {', '.join(photo_locations) if photo_locations else 'не выбраны'}\n"
    response += f"\nОжидайте выполнения запроса ⏳"

    await message.answer(response, parse_mode="Markdown")

    from loader import rag_service

    preferences = ["музеи", "парки", "кафе"]
    if "," in location:
        try:
            lat_str, lon_str = location.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            poi_text = rag_service.retrieve_documents(
                location_name="",
                preferences=preferences,
                lat=lat,
                lon=lon
            )
        except Exception:
            poi_text = "Ошибка обработки координат. Попробуйте снова."
    else:
        poi_text = rag_service.retrieve_documents(
            location_name=location,
            preferences=preferences,
            lat=None,
            lon=None
        )

    await message.answer(poi_text)
    await state.clear()
