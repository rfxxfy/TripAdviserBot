import requests
from helpers.metrics import timing, incr

class OSRMAPI:
    """
    Публичный OSRM‑сервер для пешеходного маршрута.
    Если full‑обзор не срабатывает, пробуем simplified.
    """
    BASE_URL = "https://routing.openstreetmap.de/routed-foot/route/v1"

    def __init__(self, mode: str = "foot"):
        self.mode = mode

    @timing("OSRM_search_time")
    def get_route(self, start: tuple, end: tuple, overview: str = "full"):
        start_str = f"{start[1]},{start[0]}"
        end_str   = f"{end[1]},{end[0]}"
        url = f"{self.BASE_URL}/{self.mode}/{start_str};{end_str}?overview={overview}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if resp.status_code == 200 and data.get("routes"):
                return data
            if overview == "full":
                return self.get_route(start, end, overview="simplified")
            print(f"[WARN] OSRM: нет маршрута ({overview}) между {start} и {end}")
            return {"error":"route not found","routes":[]}
        except requests.RequestException as e:
            print(f"[ERROR] OSRM request error: {e}")
            return {"error": str(e), "routes":[]}
