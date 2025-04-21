import os

BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "blacklist.txt")

def load_blacklist() -> set[str]:
    """
    Загружает все названия POI из файла blacklist.txt в множество строк в нижнем регистре.
    """
    path = os.path.abspath(BLACKLIST_FILE)
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}

def add_to_blacklist(name: str):
    """
    Добавляет новое название POI в blacklist.txt (в нижнем регистре), если его там ещё нет.
    """
    os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
    entry = name.strip().lower()
    current = load_blacklist()
    if entry in current:
        return
    with open(os.path.abspath(BLACKLIST_FILE), "a", encoding="utf-8") as f:
        f.write(entry + "\n")
