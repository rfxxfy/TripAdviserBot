import re
import requests
import urllib.parse
from typing import List, Tuple, Optional
from handlers.maps import generate_yandex_map_link, generate_yandex_map_link_from_names
from config import YANDEX_API_KEY

PLACE_NAME_OVERRIDES = {
    "Ботанический сад Дворца пионеров": "ул. Косыгина, 17, Москва, 119333",
    "Водный стадион на Химкинском водохранилище": "ул. Правды, 10, Москва, 119100"
}

CITY_BOUNDS = {
    "Москва": {"bbox": (37.32, 55.55, 37.95, 55.92)},
    "Казань": {"bbox": (48.93, 55.70, 49.28, 55.85)},
    "Нижний Новгород": {"bbox": (43.85, 56.19, 44.21, 56.40)}
}

def get_override_for_name(name: str) -> Optional[str]:
    """
    Ищет совпадение в PLACE_NAME_OVERRIDES по ключевым словам в name (без учета регистра).
    Если найдено, возвращает переопределённый адрес, иначе None.
    """
    for key, override in PLACE_NAME_OVERRIDES.items():
        if key.lower() in name.lower():
            return override
    return None

def get_coords_from_name(name: str, city: str, country: str) -> Optional[Tuple[float, float]]:
    """
    Получает точные координаты для указанного места через Яндекс Геокодер API,
    ограничивая поиск областью, заданной для города.
    Если для объекта задано переопределение, оно используется напрямую.
    Если точность результата не 'exact', выполняется альтернативный запрос.
    Возвращает координаты в формате (lat, lon) или None.
    """
    override = get_override_for_name(name)
    refined_query = override if override is not None else f"{name}, {city}, {country}"
    city_bound = CITY_BOUNDS.get(city, None)

    def query_geocoder(query: str) -> Optional[dict]:
        base_url = "https://geocode-maps.yandex.ru/1.x/?format=json"
        base_url += f"&apikey={YANDEX_API_KEY}"
        base_url += f"&geocode={urllib.parse.quote(query)}"
        base_url += "&lang=ru_RU&results=1"
        if city_bound:
            left_lon, bottom_lat, right_lon, top_lat = city_bound["bbox"]
            bbox_param = f"{left_lon},{bottom_lat}~{right_lon},{top_lat}"
            base_url += f"&bbox={bbox_param}&rspn=1"
        try:
            response = requests.get(base_url, timeout=5)
            return response.json()
        except Exception as e:
            print(f"[WARN] Ошибка запроса для '{query}': {e}")
            return None

    data = query_geocoder(refined_query)
    if not data:
        return None
    feature_members = data.get("response", {})\
                          .get("GeoObjectCollection", {})\
                          .get("featureMember", [])
    if not feature_members:
        return None
    geo_obj = feature_members[0]["GeoObject"]
    meta = geo_obj.get("metaDataProperty", {}).get("GeocoderMetaData", {})
    precision = meta.get("precision", "")
    if precision.lower() != "exact":
        alt_query = f"{name}, {city}, {country}"
        data_alt = query_geocoder(alt_query)
        if data_alt:
            feature_members_alt = data_alt.get("response", {})\
                                          .get("GeoObjectCollection", {})\
                                          .get("featureMember", [])
            if feature_members_alt:
                geo_obj = feature_members_alt[0]["GeoObject"]
    pos_str = geo_obj["Point"]["pos"]  # формат: "lon lat"
    try:
        lon, lat = map(float, pos_str.split())
        return (lat, lon)
    except Exception as e:
        print(f"[WARN] Ошибка парсинга координат для '{name}': {e}")
    return None

def clean_place_name(raw_line: str) -> str:
    """
    Очищает строку пункта маршрута от лишних данных: удаляет содержимое в круглых скобках,
    фразы о расстоянии и прочее.
    """
    name = re.split(r'[.,]', raw_line)[0]
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\bв\s+\d+(\.\d+)?\s*(км|метра?х?)\s+от\s+\S+", "", name, flags=re.IGNORECASE)
    return name.strip()

def filter_duplicate_names(names: List[str]) -> List[str]:
    seen = set()
    result = []
    for name in names:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            result.append(name)
    return result

def extract_address_blocks(day_text: str) -> List[str]:
    """
    Извлекает из текста строки, начинающиеся со слова "Адрес:".
    Возвращает список адресов.
    """
    pattern = r"Адрес:\s*(.*)"
    return re.findall(pattern, day_text, flags=re.IGNORECASE)

def extract_poi_lines(day_text: str) -> List[str]:
    """
    Извлекает из текста дня строки, начинающиеся с префикса "poi:".
    Ожидается, что каждый пункт записан в формате:
      "N. poi: <название POI>"
    Возвращает список названий без префикса.
    """
    pattern = r'^\d+\.\s+poi:\s+(.*)'
    matches = re.findall(pattern, day_text, flags=re.MULTILINE)
    return [m.strip() for m in matches]

def extract_place_name_from_text(line: str) -> str:
    """
    Эвристически извлекает название места из строки, если явное указание адреса не найдено.
    Если не удаётся найти по ключевым словам, возвращает часть строки до первой точки.
    """
    pattern = r"(?:посетите|направляйтесь|отправляйтесь|прогуляйтесь)\s+(.*?)[\.,]"
    match = re.search(pattern, line, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return line.split('.')[0].strip()

def enrich_route_with_coordinates(route_text: str, city: str, country: str, city_center: Tuple[float, float]) -> str:
    """
    Обогащает текст маршрута, формируя ссылку на Яндекс.Карты с использованием полных адресов POI.
    Если в тексте присутствуют строки "Адрес:", они используются для геокодирования.
    Если их нет, пробуем извлечь данные из строк с префиксом "poi:".
    Если и это не срабатывает, применяем эвристику для извлечения названия.
    Для каждого адреса получаем координаты с ограничением области поиска (bounding box).
    """
    day_blocks = re.split(r"(День\s+\d+:)", route_text)
    result = ""
    overall_addresses = []

    for i in range(1, len(day_blocks), 2):
        day_title = day_blocks[i].strip()
        day_body = day_blocks[i+1].strip()
        addresses = extract_address_blocks(day_body)
        if not addresses:
            addresses = [clean_place_name(x) for x in extract_poi_lines(day_body)]
        if not addresses:
            numbered_lines = re.findall(r'^\d+\.\s+(.*)', day_body, flags=re.MULTILINE)
            addresses = [extract_place_name_from_text(line) for line in numbered_lines]

        addresses = filter_duplicate_names(addresses)
        day_coords = [city_center]

        for addr in addresses:
            coord = get_coords_from_name(addr, city, country)
            if coord:
                day_coords.append(coord)
            else:
                print(f"[INFO] Координаты не найдены для '{addr}'. Используем центр города.")
                day_coords.append(city_center)
        
        if len(day_coords) >= 2:
            day_link = generate_yandex_map_link(day_coords)
            day_body += f"\n\n<a href='{day_link}'>Открыть маршрут</a>"
        else:
            day_body += "\n\n(Не удалось построить маршрут)"
        
        overall_addresses.extend(addresses)
        result += f"{day_title}\n{day_body}\n\n"
    
    overall_addresses = filter_duplicate_names(overall_addresses)
    overall_link = generate_yandex_map_link_from_names(overall_addresses, start_coords=city_center)
    result += f"<a href='{overall_link}'>Открыть общий маршрут</a>"
    return result.strip()
