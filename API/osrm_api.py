import requests

class OSRMAPI:
    BASE_URL = "https://routing.openstreetmap.de/routed-foot/route/v1"

    def __init__(self, mode: str = "foot"):
        self.mode = mode

    def get_route(self, start: tuple, end: tuple, overview: str = "full"):
        start_str = f"{start[1]},{start[0]}"
        end_str = f"{end[1]},{end[0]}"
        url = f"{self.BASE_URL}/{self.mode}/{start_str};{end_str}?overview={overview}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"OSRM HTTP {response.status_code}", "routes": []}
        except requests.exceptions.RequestException as e:
            return {"error": f"OSRM request error: {e}", "routes": []}