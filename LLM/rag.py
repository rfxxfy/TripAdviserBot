# LLM/rag.py

from typing import List, Tuple, Optional
from API.overpass_api import OverpassAPI
from API.osrm_api import OSRMAPI
from API.nominatim_api import NominatimAPI
from handlers.maps import generate_yandex_map_link
from helpers.blacklist import load_blacklist

PREFERENCE_MAP = {
    "музеи": ("tourism", "museum"),
    "парки": ("leisure", "park"),
    "рестораны": ("amenity", "restaurant"),
    "кафе": ("amenity", "cafe"),
    "магазины": ("shop", "supermarket"),
    "отели": ("tourism", "hotel"),
    "достопримечательности": ("tourism", "attraction"),
    "итальянская": ("cuisine", "italian"),
    "русская": ("cuisine", "russian"),
    "азиатская": ("cuisine", "asian"),
    "фастфуд": ("cuisine", "fast_food"),
    "вегетарианская": ("cuisine", "vegetarian"),
    "десерты": ("cuisine", "dessert"),
    "кофейни": ("amenity", "cafe"),
    "bubble tea": ("amenity", "cafe"),
}

class RAGService:
    def __init__(self):
        self.overpass   = OverpassAPI()
        self.osrm       = OSRMAPI()
        self.nominatim = NominatimAPI()
        self.blacklist = load_blacklist()

    def get_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        return self.nominatim.get_coordinates(location_name)

    def find_pois(
        self,
        lat: float,
        lon: float,
        preferences: List[str],
        default_pref: str = "достопримечательности"
    ) -> List[dict]:
        prefs = preferences or [default_pref]
        all_candidates = []
        for pref in prefs:
            osm_key, osm_val = PREFERENCE_MAP.get(pref, ("tourism", "attraction"))
            pois = self.overpass.find_popular_pois(lat, lon, osm_key, osm_val)
            for el in pois:
                name = el.get("tags", {}).get("name", "").lower()
                if name and name not in self.blacklist:
                    all_candidates.append(el)
        seen = set()
        unique = []
        for el in all_candidates:
            name = el["tags"]["name"].lower()
            if name not in seen:
                seen.add(name)
                unique.append(el)
        return unique

    def build_context(self, pois: List[dict], user_coords: Tuple[float, float]) -> str:
        if not pois:
            return "В радиусе 2 км не найдено интересных объектов."
        lines = []
        for i, el in enumerate(pois[:20], 1):
            tags = el.get("tags", {})
            name = tags.get("name")
            coord = (el.get("lat"), el.get("lon"))
            route = self.osrm.get_route(user_coords, coord)
            info = ""
            if route.get("routes"):
                dist = route["routes"][0]["distance"] / 1000
                dur  = route["routes"][0]["duration"] / 60
                info = f"{dist:.1f} км, ~{dur:.0f} мин"
            lines.append(f"{i}. {name} — {info}")
        return "Найденные места:\n" + "\n".join(lines)

    def retrieve_documents(
        self,
        location_name: Optional[str],
        preferences: List[str],
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> str:
        if lat is not None and lon is not None:
            coords = (lat, lon)
        else:
            coords = self.get_coordinates(location_name or "")
            if not coords:
                return "Не удалось найти место для поиска POI."
        pois = self.find_pois(coords[0], coords[1], preferences)
        return self.build_context(pois, coords)
