import openai
from rag import RAGService

rag_service = RAGService()

with open("tokens/hubai_token.txt", "r", encoding="utf-8") as f:
    HUBAI_API_KEY = f.read().strip()

client = openai.OpenAI(
    api_key=HUBAI_API_KEY,
    base_url="https://hubai.loe.gg/v1"
)

def generate_route(
    departure: str,
    preferences: list[str],
    route_type: str,
    days: int = 1,
    budget: float = 0.0,
    is_first_time: bool = True
) -> str:
    """
    Генерация туристического маршрута с учётом типа маршрута через HubAI.

    Параметры:
    - departure: Точка отправления (название места или координаты)
    - preferences: Список предпочтений, например ["Природные", "Городские пейзажи"]
    - route_type: Тип маршрута ("живописными местами", "питанием" и т.д.)
    - days: Количество дней (>= 1)
    - budget: Бюджет в рублях
    - is_first_time: True, если пользователь впервые в городе
    """

    retrieved_docs = rag_service.retrieve_documents(departure, preferences, route_type)

    budget_text = ""
    if budget > 0:
        budget_text = (
            f"Общий бюджет: примерно {budget} рублей на "
            f"{days} "
            f"{'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'}\n"
        )

    first_time_text = (
        "Пользователь впервые в городе — включи самые известные и обязательные к посещению достопримечательности.\n"
        if is_first_time else
        "Пользователь уже бывал в этом городе — можно предлагать менее туристические и необычные места.\n"
    )

    if days == 1:
        day_instruction = "Укажи не менее 5 разных интересных мест в течение дня.\n"
    else:
        day_instruction = "Для каждого дня предложи минимум 3 интересных места.\n"

    prompt = (
        f"Ты опытный туристический гид. Составь туристический маршрут из точки '{departure}' на {days} "
        f"{'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'} с учётом предпочтений: {', '.join(preferences)} и типа маршрута: {route_type}.\n"
        f"{first_time_text}"
        f"{budget_text}"
        f"{day_instruction}"
        "Пиши чисто, ставь абзацы между достопримечательностями и днями"
        "В каждом дне перечисли:"
        "- Названия мест, краткое описание, зачем туда идти"
        "- Примерное время пешего пути между ними"
        "- Советы по маршруту"
        "- Пешую Google Maps-ссылку на весь маршрут дня (формат: https://www.google.com/maps/dir/?api=1&travelmode=walking&origin=LAT1,LON1&waypoints=LAT2,LON2|LAT3,LON3&destination=LAT4,LON4)\n"
        "Важно: не используй никакие спецсимволы, жирный текст, заголовки, хештеги. Только обычный текст.\n"
        f"Вот справочная информация для вдохновения:\n{retrieved_docs}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты опытный туристический консультант. Никогда не используй Markdown. Пиши обычный, чистый текст."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1400
        )
        return response.choices[0].message.content.replace("**", "").replace("##", "").replace("#", "")

    except Exception as e:
        print(f"Ошибка при вызове HubAI API: {e}")
        return "Ошибка при генерации маршрута. Попробуйте ещё раз."
