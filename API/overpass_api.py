import requests

class OverpassAPI:
    """
    Класс для работы с Overpass API (OpenStreetMap).
    Можно искать разнообразные POI, указывая в запросе нужные теги (музеи, парки, рестораны и т.д.).
    """
    BASE_URL = "https://overpass-api.de/api/interpreter"

    def search_poi_in_radius(self, lat: float, lon: float, radius: int, osm_key: str, osm_value: str):
        """
        Выполняет Overpass-запрос на поиск объектов (node/way/relation)
        с заданными osm_key/osm_value в радиусе (в метрах) от точки (lat, lon).
        """
        query = f"""
        [out:json];
        (
          node["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
          way["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
          relation["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
        );
        out center;
        """
        headers = {
            "User-Agent": "Telegram-Bot/1.0"
        }
        try:
            response = requests.post(self.BASE_URL, data={"data": query}, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Overpass error: {e}")
            return {"elements": []}
