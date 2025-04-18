with open("tokens/token.txt", "r") as f:
    TOKEN = f.read().strip()

with open("tokens/ai_token.txt", "r") as f:
    API_KEY = f.read().strip()

with open("tokens/yandex_api_key.txt", "r", encoding="utf-8") as f:
    YANDEX_API_KEY = f.read().strip()