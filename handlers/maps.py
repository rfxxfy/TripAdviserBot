import re
import urllib.parse
from geopy.distance import geodesic

def determine_transport_type(coords: list[tuple[float, float]]) -> str:
    """
    Определяет тип маршрута (пешком или общественным транспортом)
    по суммарному расстоянию между точками.
    Если суммарное расстояние > 4 км, возвращает 'mt', иначе — 'tt'.
    """
    if len(coords) < 2:
        return "tt"
    total_dist = sum(geodesic(coords[i], coords[i+1]).km for i in range(len(coords)-1))
    return "mt" if total_dist > 4 else "tt"

def generate_yandex_map_link(coords: list[tuple[float, float]]) -> str:
    """
    Генерирует ссылку на Яндекс.Карты, используя координаты маршрута.
    Точки передаются в параметре rtext в формате: lat,lon~lat,lon~...,
    а тип маршрута определяется на основе суммарного расстояния.
    """
    if len(coords) < 2:
        return ""
    transport = determine_transport_type(coords)
    rtext = "~".join(f"{lat},{lon}" for lat, lon in coords)
    return f"https://yandex.ru/maps/?mode=routes&rtext={rtext}&rtt={transport}"

def generate_yandex_map_link_from_names(points: list[str], start_coords: tuple[float, float] = None) -> str:
    """
    Генерирует ссылку на Яндекс.Карты, используя текстовые названия точек.
    Если указан start_coords, он используется как первая точка маршрута (в формате lat,lon),
    а последующие точки передаются как URL-энкодированные строки.
    """
    parts = []
    if start_coords:
        parts.append(f"{start_coords[0]},{start_coords[1]}")
    for p in points:
        parts.append(urllib.parse.quote(p))
    rtext = "~".join(parts)
    return f"https://yandex.ru/maps/?rtext={rtext}&rtt=tt"

def extract_coords_blocks(text: str) -> list[tuple[float, float]]:
    """
    Извлекает из строки все группы вида (lat, lon).
    Пример: "Координаты: (55.7558, 37.6173), (55.7520, 37.6000)"
    -> [(55.7558, 37.6173), (55.752, 37.6)]
    """
    pattern = r"\(\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\)"
    matches = re.findall(pattern, text)
    return [(float(lat), float(lon)) for lat, lon in matches]
