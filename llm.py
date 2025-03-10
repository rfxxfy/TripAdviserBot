import openai
from rag import retrieve_documents


def generate_route(departure: str, preferences: list[str]) -> str:
    search_query = f"{departure} " + " ".join(preferences)
    retrieved_docs = retrieve_documents(search_query)

    prompt = (
        f"Составь подробный туристический маршрут, начиная с точки отправления '{departure}'.\n"
        f"Учитывай следующие предпочтения: {', '.join(preferences)}.\n"
        "Используй следующую справочную информацию:\n"
        f"{retrieved_docs}\n\n"
        "В маршруте укажи рекомендуемые остановки, краткие описания и советы для путешественника."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты опытный туристический консультант."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        answer = response["choices"][0]["message"]["content"]
    except Exception as e:
        answer = "Произошла ошибка при генерации маршрута. Пожалуйста, попробуйте ещё раз."
        print(f"Ошибка при вызове OpenAI API: {e}")
    return answer
