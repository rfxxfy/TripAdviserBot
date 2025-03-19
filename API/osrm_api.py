import requests

class OSRMAPI:
    """
    Класс для взаимодействия с публичным OSRM-сервером.
    """

    BASE_URL = "https://routing.openstreetmap.de/routed-foot/route/v1"

    def __init__(self, mode: str = "foot"):
        self.mode = mode

    def get_route(self, start: tuple, end: tuple, overview: str = "full"):
        """
        Строит маршрут между двумя точками (lat, lon) -> (lat, lon).
        Возвращает JSON, где есть поле "routes" с расстоянием и временем.
        """
        start_str = f"{start[1]},{start[0]}"  # (lon,lat)
        end_str = f"{end[1]},{end[0]}"
        url = f"{self.BASE_URL}/{self.mode}/{start_str};{end_str}?overview={overview}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "routes" in data and data["routes"]:
                    return data
                else:
                    print(f"OSRM: Нет маршрута между {start} и {end}")
                    return {"error": "Маршрут не найден", "routes": []}
            else:
                print(f"OSRM: Ошибка HTTP {response.status_code}")
                return {"error": f"OSRM HTTP {response.status_code}", "routes": []}
        except requests.exceptions.RequestException as e:
            print(f"OSRM: Ошибка сети {e}")
            return {"error": f"OSRM request error: {e}", "routes": []}