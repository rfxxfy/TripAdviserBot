from loader import client

def validate_route_content(route_text: str, budget: float) -> str:
    """
    Отправляет сгенерированный маршрут второму LLM для доработки и проверки.
    Требования:
    1. Вернуть маршрут в виде текстового описания с рекомендациями, описаниями и временными данными.
    2. Для каждой достопримечательности указать время посещения и время пешего перехода от предыдущей точки, при этом временные данные выделить жирным (например, **30 минут**).
    3. Сохранить общую Google Maps-ссылку для всего маршрута.
    4. Если маршрут предназначен для одного дня, суммарное время маршрута (с учётом посещений и переходов) должно составлять минимум **6 часов**.
    5. Если маршрут содержит рекомендации по ресторанам, их средний чек должен соответствовать заданному бюджету; при завышенных ценах – заменить на более доступные варианты.
    6. Вернуть только исправленный маршрут без каких-либо пояснительных комментариев.
    """
    prompt = (
        "Исправь и доработай следующий туристический маршрут так, чтобы:\n"
        "1. Маршрут был представлен в виде текстового описания, включающего подробное описание достопримечательностей и рекомендации.\n"
        "2. Для каждой точки маршрута указывай время, необходимое для её посещения, и время пешего перехода от предыдущей точки.\n"
        "3. Общая Google Maps-ссылка для маршрута остаётся одной и корректной.\n"
        "5. Если маршрут содержит рекомендации по ресторанам, средний чек этих заведений должен быть ниже заданного бюджета. При обнаружении ресторанов с завышенными ценами замени их на более доступные варианты.\n"
        "6. Важно: не используй никакие спецсимволы, жирный текст, заголовки, хештеги. Только обычный текст.\n"
        "7. Время маршрута по каждому дню, включая все переходы и посещения, должно быть не менее 6 часов.\n"
        "8. В конце каждого маршрута указывай примерное время, на которое он рассчитан.\n"
        "Верни только конечный вариант маршрута без дополнительных комментариев о внесённых изменениях.\n\n"
        f"{route_text}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты опытный туристический консультант и редактор. "
                        "Исправь маршрут согласно заданным требованиям и верни только конечный вариант маршрута."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1400
        )
        validated_text = response.choices[0].message.content
        return validated_text
    except Exception as e:
        print(f"[ERROR] Ошибка валидации маршрута: {e}")
        return route_text
