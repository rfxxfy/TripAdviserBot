from LLM.rag import RAGService
from LLM.validator import validate_route_content
from loader import client

rag_service = RAGService()


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

    day_instruction = (
        "Укажи не менее 5 разных интересных мест в течение дня.\n"
        if days == 1 else
        "Для каждого дня предложи минимум 3 интересных места.\n"
    )

    prompt = (
        f"Ты опытный туристический гид. Составь туристический маршрут из точки '{departure}' на {days} "
        f"{'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'} с учётом предпочтений: {', '.join(preferences)} и типа маршрута: {route_type}.\n"
        f"{first_time_text}"
        f"{budget_text}"
        f"{day_instruction}"
        "Пиши чисто, ставь абзацы между достопримечательностями и днями. "
        "В каждом дне перечисли:\n"
        "- Названия мест, краткое описание, зачем туда идти\n"
        "- Примерное время пешего пути между ними\n"
        "- Советы по маршруту\n"
        "- Пешую Google Maps-ссылку на весь маршрут дня (формат: https://www.google.com/maps/dir/?api=1&travelmode=walking&origin=LAT1,LON1&waypoints=LAT2,LON2|LAT3,LON3&destination=LAT4,LON4)\n"
        f"Вот справочная информация для вдохновения:\n{retrieved_docs}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты опытный туристический консультант. Никогда не используй Markdown. Пиши обычный, чистый текст."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1400
        )
        initial_route = response.choices[0].message.content.replace("**", "").replace("##", "").replace("#", "")
        validated_route = validate_route_content(initial_route, budget)
        return validated_route

    except Exception as e:
        print(f"Ошибка при вызове HubAI API: {e}")
        return "Ошибка при генерации маршрута. Попробуйте ещё раз."
