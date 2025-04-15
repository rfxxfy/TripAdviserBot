import openai
import re
from loader import client
from LLM.postprocess import enrich_route_with_coordinates

def extract_day_blocks(text: str) -> list[tuple[str, str]]:
    blocks = re.split(r"(День\s+\d+:)", text)
    return [(blocks[i].strip(), blocks[i+1].strip()) for i in range(1, len(blocks), 2)]

def validate_route_content(
    route_text: str,
    budget: float,
    city: str,
    country: str,
    city_center: tuple[float, float],
    model: str = "gpt-4-turbo"
) -> str:
    if not route_text.strip():
        return "Ошибка: пустой маршрут."

    prompt = (
        "Проверь и доработай туристический маршрут по следующим требованиям:\n"
        "1. Не используй markdown, жирный текст или хештеги.\n"
        "2. В каждом дне должно быть минимум 3–5 точек интереса.\n"
        "3. Каждый пункт маршрута должен содержать строку с полным адресом в формате:\n"
        "   Адрес: <полный адрес, включая город и страну, обязателен ТОЧНАЯ УЛИЦА И ДОМ>\n"
        "   Для маршрута крайне важен точный адрес, это самая главная твоя задача! прикрепи примерное"
        "   если невозможно определить точный\n"
        "4. В конце каждого дня маршрута обязательно добавь строку с координатами в формате:\n"
        "   Координаты: (lat, lon), (lat, lon), ...\n"
        "   Если координаты невозможно определить, укажи примерные (например, центр города).\n"
        f"Бюджет пользователя: {budget} рублей\n\n"
        f"{route_text}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ты редактор туристических маршрутов. Пиши чистый текст и обязательно добавляй адреса и координаты для каждой остановки."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        validated_text = response.choices[0].message.content.strip()
        day_blocks = extract_day_blocks(validated_text)
        for day_title, day_body in day_blocks:
            if not re.search(r"Адрес:\s*", day_body, flags=re.IGNORECASE):
                return ("Ошибка: в маршруте отсутствуют адреса для остановок. "
                        "Убедитесь, что каждый пункт маршрута содержит строку 'Адрес: <полный адрес>'.")

        enriched_text = enrich_route_with_coordinates(
            validated_text,
            city=city,
            country=country,
            city_center=city_center
        )
        final_output = ""
        for day_title, day_body in extract_day_blocks(enriched_text):
            day_body_clean = re.sub(r"(Координаты|Итоговые координаты).*?:.*?(\n|$)", "", day_body)
            final_output += f"{day_title}\n{day_body_clean.strip()}\n\n"
        return final_output.strip() if final_output.strip() else "Ошибка: не удалось собрать маршрут."
    except Exception as e:
        print(f"[ERROR] Ошибка валидации маршрута: {e}")
        return "Ошибка валидации маршрута. Попробуйте позже."
