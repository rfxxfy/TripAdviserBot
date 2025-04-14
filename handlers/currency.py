import re
from aiogram import types
from aiogram.fsm.context import FSMContext
from states.travel_states import TravelForm
from keyboards.inline_keyboards import get_back_to_main_keyboard
from loader import rag_service
from database.db import save_location
from API.overpass_api import OverpassAPI

async def currency_exchange(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    
    message = await callback.message.answer(
        "📍 Пожалуйста, отправьте свою геопозицию или введите адрес, чтобы найти ближайшие банки",
        reply_markup=get_back_to_main_keyboard()
    )
    
    await state.update_data(last_message_with_keyboard_id=message.message_id)
    await state.set_state(TravelForm.waiting_for_currency_location)
    await callback.answer()


async def process_currency_location(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != TravelForm.waiting_for_currency_location:
        return
    
    coords = None
    location_text = "не определена"
    
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        coords = (lat, lon)
        location_text = f"{lat}, {lon}"
        
    elif message.text:
        text_input = message.text.strip()
        decimal_pattern = r'^(-?\d+(\.\d+)?)[,\s]+(-?\d+(\.\d+)?)$'
        decimal_match = re.match(decimal_pattern, text_input)
        
        if decimal_match:
            try:
                lat = float(decimal_match.group(1).replace(',', '.'))
                lon = float(decimal_match.group(3).replace(',', '.'))
                
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    await message.answer("🚨 Ошибка: координаты вне допустимого диапазона.\nШирота должна быть от -90 до 90, долгота от -180 до 180.")
                    return
                
                coords = (lat, lon)
                location_text = text_input
            except ValueError:
                pass
        else:
            coords = rag_service.get_coordinates(text_input)
            if coords:
                location_text = text_input
    
    if not coords:
        await message.answer("🚨 Не удалось определить местоположение. Пожалуйста, отправьте точные координаты или название места.")
        return
    
    session_id = (await state.get_data()).get("session_id")
    if session_id:
        save_location(session_id, location_text, coords[0], coords[1])
    
    await find_banks_and_route(message, coords)
    
    await state.clear()

async def find_banks_and_route(message: types.Message, user_coords: tuple):
    user_lat, user_lon = user_coords
    await message.answer("🏦 Ищем ближайшие банки...")
    
    overpass = OverpassAPI()
    
    banks_data = overpass.search_poi_in_radius(user_lat, user_lon, 3000, "amenity", "bank", limit=10)
    valid_banks = [
        bank for bank in banks_data.get("elements", []) 
        if bank.get("tags", {}).get("name")
    ]

    reply = ""
    counter = 0

    if valid_banks:
        reply += "🏦 *Найденные банки:*\n\n"
        for bank in valid_banks:
            counter += 1
            tags = bank.get("tags", {})
            name = tags.get("name", "Неизвестный банк")
            
            bank_lat = bank.get("lat") if bank.get("type") == "node" else bank.get("center", {}).get("lat")
            bank_lon = bank.get("lon") if bank.get("type") == "node" else bank.get("center", {}).get("lon")
            
            reply += f"{counter}. *{name}*\n"
            
            address = f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip()
            if address:
                reply += f"   📍 {address}\n"

            if tags.get("opening_hours"):
                reply += f"   🕒 {tags.get('opening_hours')}\n"

            if bank_lat and bank_lon:
                route_link = f"https://yandex.ru/maps/?rtext={user_lat},{user_lon}~{bank_lat},{bank_lon}&rtt=pd"
                reply += f"   🚶 [Построить маршрут]({route_link})\n"
            
            reply += "\n"

    if not reply:
        await message.answer("❌ Не удалось найти банки поблизости. Попробуйте другую локацию.")
    else:
        MAX_LENGTH = 4096
        for i in range(0, len(reply), MAX_LENGTH):
            await message.answer(reply[i:i+MAX_LENGTH], parse_mode="Markdown", disable_web_page_preview=True)
        
    await message.answer("Для возврата в главное меню нажмите кнопку ниже:", reply_markup=get_back_to_main_keyboard())