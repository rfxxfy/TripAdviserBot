"""
Этот файл содержит обработчики состояний и логику выбора параметров.
"""
from aiogram import types
from aiogram.fsm.context import FSMContext
from states.travel_states import TravelForm
from keyboards.inline_keyboards import get_photo_locations_keyboard, get_back_to_main_keyboard, PHOTO_OPTIONS


async def start_parameter_collection(
        callback: types.CallbackQuery,
        selected_routes: dict,
        state: FSMContext):
    """
    Сохраняет выбранные маршруты и формирует порядок вопросов.
    Затем запрашивает у пользователя геолокацию/адрес отправления.
    """
    questions_order = ["location","budget","days"]
    if selected_routes.get("photo"):
        questions_order.append("photo")

    await state.update_data(selected_routes=selected_routes, questions_order=questions_order, question_index=0)

    message = await callback.message.answer(
        "📍 Пожалуйста, отправьте свою геолокацию или введите адрес отправления.",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.update_data(last_message_with_keyboard_id=message.message_id)
    await state.set_state(TravelForm.waiting_for_location)
    await callback.answer()


async def ask_next_question(message: types.Message, state: FSMContext):
    """
    Задаёт следующий вопрос пользователю на основе данных, сохранённых в состоянии.
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
        await message.answer("📆 На сколько дней вы планируете путешествовать?")
        await state.set_state(TravelForm.waiting_for_days)
    else:
        await finish_parameters_collection(message, state)


async def process_location(message: types.Message, state: FSMContext):
    """
    Сохраняет локацию и переходит к следующему этапу.
    """
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
    Сохраняет введённый бюджет и переходит к следующему вопросу.
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


async def toggle_photo_locations(
        callback: types.CallbackQuery,
        state: FSMContext):
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
    await callback.message.edit_reply_markup(
        reply_markup=get_photo_locations_keyboard(selected, PHOTO_OPTIONS)
    )
    await callback.answer("Обновлено!")


async def confirm_photo_locations(
        callback: types.CallbackQuery,
        state: FSMContext):
    """
    Завершает этап выбора фото‑локаций и переходит к следующему вопросу.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    question_index = data.get("question_index", 0) + 1
    await state.update_data(question_index=question_index)
    await callback.answer("Выбор фото-локаций подтверждён!")
    await ask_next_question(callback.message, state)


async def process_days(message: types.Message, state: FSMContext):
    """
    Сохраняет введённое количество дней и завершает сбор параметров.
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


async def finish_parameters_collection(
        message: types.Message,
        state: FSMContext):
    """
    Завершает этап выбора фото‑локаций и переходит к следующему вопросу.
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

    await message.answer(response, parse_mode="Markdown")
    await state.clear()
