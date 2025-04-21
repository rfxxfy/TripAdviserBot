import re
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from states.travel_states import TravelForm
from loader import rag_service
from API.overpass_api import OverpassAPI
from database.db import save_location
from keyboards.inline_keyboards import get_back_to_main_keyboard


async def currency_exchange(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    msg = await callback.message.answer(
        "📍 Отправьте геолокацию или введите адрес для поиска банков",
        reply_markup=kb
    )
    await state.update_data(last_message_with_keyboard_id=msg.message_id)
    await state.set_state(TravelForm.waiting_for_currency_location)
    await callback.answer()


async def process_currency_location(message: types.Message, state: FSMContext):
    coords = None
    loc = None
    if message.location:
        coords = (message.location.latitude, message.location.longitude)
        loc = f"{coords[0]}, {coords[1]}"
    else:
        text = message.text.strip()
        if re.match(r'^-?\d+(?:\.\d+)?[,\s]+-?\d+(?:\.\d+)?$', text):
            parts = re.split(r"[\s,]+", text)
            coords = (float(parts[0]), float(parts[1]))
            loc = text
        else:
            coords = rag_service.get_coordinates(text)
            loc = text if coords else None

    if not coords:
        await message.answer("🚨 Не удалось определить местоположение.")
        return

    data = await state.get_data()
    session_id = data.get("session_id")
    if session_id:
        save_location(session_id, loc, coords[0], coords[1])

    overpass = OverpassAPI()
    elems = overpass.search_poi_in_radius(coords[0], coords[1], 3000, "amenity", "bank", limit=10)
    banks = [b for b in elems if b.get("tags", {}).get("name")]

    if not banks:
        await message.answer("❌ Банки не найдены поблизости.", reply_markup=ReplyKeyboardRemove())
    else:
        text = "🏦 Найденные банки:\n\n"
        for i, b in enumerate(banks[:10], 1):
            tags = b.get("tags", {})
            name = tags.get("name", "Без названия")
            lat = b.get("lat") or b.get("center", {}).get("lat")
            lon = b.get("lon") or b.get("center", {}).get("lon")
            addr = f"{tags.get('addr:street','')} {tags.get('addr:housenumber','')}".strip()
            hours = tags.get("opening_hours", "")
            route = f"https://yandex.ru/maps/?rtext={coords[0]},{coords[1]}~{lat},{lon}&rtt=pd"
            text += f"{i}. *{name}*\n"
            if addr:
                text += f"   📍 {addr}\n"
            if hours:
                text += f"   🕒 {hours}\n"
            text += f"   🚶 [Маршрут]({route})\n\n"

        for chunk in [text[j:j+4000] for j in range(0, len(text), 4000)]:
            await message.answer(
                chunk,
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=ReplyKeyboardRemove()
            )

    await message.answer(
        "Для возврата в главное меню нажмите:",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.clear()
