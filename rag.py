from typing import List, Tuple, Optional
from API.overpass_api import OverpassAPI
from API.osrm_api import OSRMAPI
from API.nominatim_api import NominatimAPI

PREFERENCE_MAP = {
    "музеи": ("tourism", "museum"),
    "парки": ("leisure", "park"),
    "рестораны": ("amenity", "restaurant"),
    "кафе": ("amenity", "cafe"),
    "достопримечательности": ("tourism", "attraction"),
}

class RAGService:
    def __init__(self):
        self.overpass = OverpassAPI()
        self.osrm = OSRMAPI(mode="foot")
        self.nominatim = NominatimAPI()

    def get_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Определяем координаты города через Nominatim.
        Если не найдено, возвращаем None.
        """
        coords = self.nominatim.get_coordinates(location_name)
        return coords

    def find_pois(self, lat: float, lon: float, preferences: List[str], radius: int = 2000) -> List[dict]:
        """
        Ищем POI в радиусе radius метров от заданных координат
        по указанным в preferences категориям (музеи, парки и т.п.).
        """
        results = []
        if not preferences:
            preferences = ["достопримечательности"]

        for pref in preferences:
            osm_key, osm_value = PREFERENCE_MAP.get(pref, ("tourism", "attraction"))
            poi_data = self.overpass.search_poi_in_radius(lat, lon, radius, osm_key, osm_value)
            results.extend(poi_data.get("elements", []))
        return results

    def build_context(self, pois: List[dict], user_coords: Tuple[float, float]) -> str:
        """
        Формируем текстовый список ближайших POI (до 5 штук) с расстоянием и примерным временем пешего пути.
        """
        if not pois:
            return "В радиусе 2 км не найдено интересных объектов по заданным предпочтениям."

        lines = []
        for i, el in enumerate(pois[:5], 1):
            tags = el.get("tags", {})
            name = tags.get("name", "Без названия")

            if el["type"] == "node":
                lat_poi, lon_poi = el["lat"], el["lon"]
            else:
                center = el.get("center", {})
                lat_poi = center.get("lat", 0)
                lon_poi = center.get("lon", 0)

            route_json = self.osrm.get_route(user_coords, (lat_poi, lon_poi))
            if route_json.get("routes"):
                dist_m = route_json["routes"][0]["distance"]
                dur_s = route_json["routes"][0]["duration"]
                dist_km = dist_m / 1000
                dur_min = dur_s / 60
                info = f"{dist_km:.2f} км, ~{dur_min:.0f} мин пешком"
            else:
                info = "Маршрут не найден"

            lines.append(f"{i}. {name} — {info}")

        return "Найденные места (топ-5):\n" + "\n".join(lines)

    def retrieve_documents(
        self,
        location_name: str,
        preferences: List[str],
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> str:
        """
        Возвращает список ближайших POI (в текстовом виде) либо сообщение об ошибке.
        Если lat/lon переданы, используем их напрямую.
        Иначе определяем координаты по location_name (через Nominatim).
        """
        if lat is not None and lon is not None:
            coords = (lat, lon)
        else:
            coords = self.get_coordinates(location_name)
            if not coords:
                return "Не удалось найти место, попробуйте другой город."

        pois = self.find_pois(coords[0], coords[1], preferences, radius=2000)
        return self.build_context(pois, coords)