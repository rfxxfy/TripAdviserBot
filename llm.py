import openai
from rag import RAGService
from rag import RAGService

rag_service = RAGService()
rag_service = RAGService()

def generate_route(departure: str, preferences: list[str]) -> str:
    """
    Генерация туристического маршрута на основе данных из RAGService и модели OpenAI.
    """
    retrieved_docs = rag_service.retrieve_documents(
        location_name=departure,
        preferences=preferences
    )
    """
    Генерация туристического маршрута на основе данных из RAGService и модели OpenAI.
    """
    # Получаем "справочную информацию" (POI) через RAGService
    retrieved_docs = rag_service.retrieve_documents(
        location_name=departure,
        preferences=preferences
    )

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