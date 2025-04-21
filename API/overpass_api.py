import requests
from helpers.metrics import timing, incr

class OverpassAPI:
    """
    Поиск POI через Overpass, с фильтрацией и динамическим радиусом.
    """

    BASE_URL = "https://overpass-api.de/api/interpreter"

    @timing("overpass_search_time")
    def search_poi_in_radius(self, lat, lon, radius, osm_key, osm_value, limit=50):
        """
        Базовый поиск (возвращаем побольше, дальше фильтруем).
        """
        query = f"""
        [out:json][timeout:25];
        (
          node["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
          way ["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
          relation["{osm_key}"="{osm_value}"](around:{radius},{lat},{lon});
        );
        out center;
        """
        try:
            resp = requests.get(self.BASE_URL, params={"data": query}, timeout=25)
            data = resp.json() if resp.status_code == 200 else {}
            elems = data.get("elements", [])
            return elems
        except requests.RequestException as e:
            print(f"[ERROR] Overpass API network: {e}")
            return []

    def find_popular_pois(self, lat, lon, osm_key, osm_value,
                          initial_radius=1000, step=1000, max_radius=5000, limit=20):
        """
        Динамический радиус + оценка важности:
        wikidata/wikipedia + historic + addr:street.
        """
        radius = initial_radius
        candidates = []
        while radius <= max_radius:
            elems = self.search_poi_in_radius(lat, lon, radius, osm_key, osm_value, limit*3)
            scored = []
            for el in elems:
                tags = el.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue
                score = 1
                if tags.get("wikidata") or tags.get("wikipedia"):
                    score += 5
                if tags.get("historic") == "yes":
                    score += 2
                if tags.get("addr:street"):
                    score += 1
                scored.append((score, el))
            scored.sort(key=lambda x: -x[0])
            candidates = [el for _, el in scored]
            if len(candidates) >= limit or radius == max_radius:
                break
            radius += step
        return candidates[:limit]
