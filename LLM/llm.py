import openai
from LLM.rag import RAGService
from LLM.validator import validate_route_content
from handlers.maps import generate_yandex_map_link
from geopy.geocoders import Nominatim

rag_service = RAGService()

with open("tokens/ai_token.txt", "r", encoding="utf-8") as f:
    HUBAI_API_KEY = f.read().strip()

client = openai.OpenAI(
    api_key=HUBAI_API_KEY,
    base_url="https://hubai.loe.gg/v1"
)

DEFAULT_MODEL = "gpt-3.5-turbo"

def get_city_and_country_from_coords(lat: float, lon: float) -> tuple[str, str]:
    """
    Возвращает кортеж (город, страна) по заданным координатам.
    """
    try:
        geolocator = Nominatim(user_agent="tripbot")
        location = geolocator.reverse((lat, lon), language="ru", timeout=10)
        address = location.raw.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village") or address.get("state") or "неизвестный город"
        country = address.get("country", "неизвестная страна")
        return city, country
    except Exception as e:
        print(f"[ERROR] Не удалось определить город и страну по координатам: {e}")
        return "неизвестный город", "неизвестная страна"

def generate_route(
    departure: str,
    preferences: list[str],
    route_type: str,
    days: int = 1,
    budget: float = 0.0,
    is_first_time: bool = True,
    model: str = DEFAULT_MODEL
) -> str:
    coords = rag_service.get_coordinates(departure)
    if not coords:
        return "Похоже, вы указали некорректное или несуществующее место. Пожалуйста, введите реальный город."

    lat, lon = coords
    is_coords_input = "," in departure

    city_name, country = get_city_and_country_from_coords(lat, lon)
    retrieved_docs = rag_service.retrieve_documents(
        location_name=city_name,
        preferences=preferences,
        lat=lat,
        lon=lon
    )

    if len(retrieved_docs) > 3000:
        retrieved_docs = retrieved_docs[:3000] + "\n..."

    budget_text = ""
    if budget > 0:
        daily_budget = budget / days
        min_spend = int(daily_budget * 0.7)
        budget_text = (
            f"Общий бюджет: {budget} рублей на {days} дн. (~{int(daily_budget)} руб/день)\n"
            f"Желательно тратить не менее 70% дневного бюджета (от {min_spend} руб/день)\n"
            "Предусмотри кафе, мероприятия, музеи или прогулки с затратами\n"
        )

    first_time_text = (
        f"Пользователь впервые в городе — включи известные достопримечательности, например\n"
        f"Биг Бен для Лондона, Красная площадь для Москвы, Эйфелева Башня в Париже... дальше по аналогии"
        if is_first_time else
        "Пользователь уже был в городе — предложи менее туристические, интересные места\n"
    )

    day_instruction = (
        "Укажи не менее 5 интересных мест в день\n"
        if days == 1 else
        "Для каждого дня предложи минимум 3 интересных места\n"
    )

    if is_coords_input:
        start_point_text = (
            f"Начинай маршрут каждый день из точки координат {lat}, {lon} — это местоположение пользователя (например, отель).\n"
            "Первая точка маршрута всегда должна быть недалеко от неё.\n"
        )
    else:
        start_point_text = ""

    prompt = (
        f"Составь маршрут из точки '{city_name}' на {days} "
        f"{'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'}, "
        f"учитывая предпочтения: {', '.join(preferences)} и тип маршрута: {route_type}.\n"
        f"{first_time_text}"
        f"{budget_text}"
        f"{day_instruction}"
        f"{start_point_text}"
        "Каждый день маршрута начинай с заголовка 'День N:', где N — номер дня.\n"
        "Внутри каждого дня используй нумерацию достопримечательностей (1, 2, 3...) для удобства восприятия.\n"
        "Для каждого пункта маршрута обязательно укажи полное название места и на отдельной строке его полный адрес в формате:\n"
        "Адрес: <полный адрес, включая город и страну>\n"
        "Если адрес определить невозможно, укажи примерный адрес (например, центр города).\n"
        "В конце каждого дня маршрута обязательно добавь строку с координатами в формате:\n"
        "Координаты: (lat, lon), (lat, lon), ...\n"
        "Если координаты невозможно определить — всё равно вставь примерные (например, центр города), иначе маршрут не сработает.\n"
        "Координаты критичны для построения карты. Без них маршрут будет считаться ошибочным!\n"
        "Не используй markdown, жирный текст или хештеги.\n"
        f"\nВот справочная информация:\n{retrieved_docs}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ты туристический консультант. Отвечай чистым текстом, без Markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1600
        )
        content = response.choices[0].message.content.strip()
        if not content:
            print("[ERROR] Модель вернула пустой ответ")
            return "Ошибка: модель не вернула маршрут. Попробуйте позже"
        return validate_route_content(
            content,
            budget,
            city=city_name,
            country=country,
            city_center=(lat, lon),
            model=model
        )
    except Exception as e:
        print(f"[ERROR] Ошибка при вызове HubAI API: {e}")
        return "Ошибка при генерации маршрута. Попробуйте ещё раз"
