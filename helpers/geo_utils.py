from math import radians, sin, cos, sqrt, asin
from typing import Tuple

def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Расстояние в км между двумя точками (lat, lon).
    """
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c

def format_coord(coord: Tuple[float, float]) -> str:
    """
    Форматирует координаты «lat,lon».
    """
    return f"{coord[0]:.6f},{coord[1]:.6f}"
