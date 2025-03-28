from typing import List, Tuple, Optional
from API.overpass_api import OverpassAPI
from API.osrm_api import OSRMAPI
from API.nominatim_api import NominatimAPI

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
}

class RAGService:
    def __init__(self):
        self.overpass = OverpassAPI()
        self.osrm = OSRMAPI(mode="foot")
        self.nominatim = NominatimAPI()

    def get_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        coords = self.nominatim.get_coordinates(location_name)
        if not coords:
            print(f"[ERROR] Не удалось получить координаты для {location_name}")
        return coords

    def find_pois(self, lat: float, lon: float, preferences: List[str], radius: int = 2000) -> List[dict]:
        results = []
        if not preferences:
            preferences = ["достопримечательности"]

        for pref in preferences:
            osm_key, osm_value = PREFERENCE_MAP.get(pref, ("tourism", "attraction"))
            poi_data = self.overpass.search_poi_in_radius(lat, lon, radius, osm_key, osm_value)

            if "error" in poi_data:
                print(f"[ERROR] Ошибка Overpass: {poi_data['error']}")

            filtered_pois = [
                el for el in poi_data.get("elements", []) if "name" in el.get("tags", {})
            ]
            results.extend(filtered_pois)

        return results

    def build_context(self, pois: List[dict], user_coords: Tuple[float, float]) -> str:
        if not pois:
            return "В радиусе 2 км не найдено интересных объектов по заданным предпочтениям"

        lines = []
        for i, el in enumerate(pois[:20], 1):
            tags = el.get("tags", {})
            name = tags.get("name")

            if not name:
                continue

            lat_poi, lon_poi = 0, 0
            if el["type"] == "node":
                lat_poi, lon_poi = el["lat"], el["lon"]
            else:
                center = el.get("center", {})
                lat_poi = center.get("lat", 0)
                lon_poi = center.get("lon", 0)

            route_json = self.osrm.get_route(user_coords, (lat_poi, lon_poi))
            if route_json.get("error"):
                print(f"[ERROR] OSRM: {route_json['error']}")

            if route_json.get("routes"):
                dist_m = route_json["routes"][0]["distance"]
                dur_s = route_json["routes"][0]["duration"]
                dist_km = dist_m / 1000
                dur_min = dur_s / 60
                info = f"{dist_km:.2f} км, ~{dur_min:.0f} мин"
            else:
                info = "Маршрут не найден"

            lines.append(f"{i}. {name} — {info}")

        return "Найденные места (топ-20):\n" + "\n".join(lines)

    def retrieve_documents(
        self,
        location_name: Optional[str],
        preferences: List[str],
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> str:
        if lat is not None and lon is not None:
            coords = (lat, lon)
            print(f"[INFO] Используем переданные координаты: {coords}")
        else:
            if not location_name:
                return "Ошибка: Не указано место для поиска"
            coords = self.get_coordinates(location_name)
            if not coords:
                return "Не удалось найти место, попробуйте другой город"

        pois = self.find_pois(coords[0], coords[1], preferences, radius=2000)
        return self.build_context(pois, coords)
