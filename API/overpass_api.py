import requests

class OverpassAPI:
    """
    Класс для работы с Overpass API (OSM)
    Используется для поиска POI в радиусе от заданной точки
    """

    BASE_URL = "https://overpass-api.de/api/interpreter"

    def search_poi_in_radius(self, lat: float, lon: float, radius: int, osm_key: str, osm_value: str, limit: int = 20):
        """
        Ищет POI (точки интереса) в радиусе (в метрах) вокруг точки (lat, lon) с указанным тегом
        :param lat: Широта точки центра поиска
        :param lon: Долгота точки центра поиска
        :param radius: Радиус поиска в метрах
        :param osm_key: Ключ OSM (tourism", "amenity")
        :param osm_value: Значение OSM ("museum", "cafe")
        :param limit: Максимальное количество найденных объектов (default: 20)
        :return: JSON с полем 'elements', содержащими найденные объекты
        """
        query = f"""
        [out:json][timeout:25];
        (
          node["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
          way["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
          relation["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
        );
        out center;
        """

        try:
            response = requests.get(self.BASE_URL, params={"data": query}, timeout=25)
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])

                filtered_elements = [el for el in elements if "name" in el.get("tags", {})]

                if not filtered_elements:
                    print(f"[INFO] Overpass: Не найдено объектов с названием по запросу ({osm_key}={osm_value})")

                return {"elements": filtered_elements[:limit]}
            else:
                print(f"[ERROR] Overpass API: Ошибка HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}", "elements": []}
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Overpass API: Ошибка сети {e}")
            return {"error": f"Ошибка сети: {e}", "elements": []}