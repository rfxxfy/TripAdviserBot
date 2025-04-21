from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from functools import lru_cache
import time
from helpers.decorators import retry
from helpers.cache import cached
from helpers.metrics import timing, incr

class NominatimAPI:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="TripAdvisorBot/1.0 (mike@example.com)")

    @timing("nominatim_search_time")
    @cached(maxsize=128)
    @retry(times=3, delay=1.0, exceptions=(GeocoderTimedOut, GeocoderServiceError))
    def get_coordinates(self, location_name: str):
        """
        Кэшированный запрос к Nominatim с 3‑кратной попыткой.
        """
        for attempt in range(3):
            time.sleep(0)
            loc = self.geolocator.geocode(location_name, timeout=10)
            if loc:
                return loc.latitude, loc.longitude
            else:
                print(f"[ERROR] Nominatim: не найдено '{location_name}'")
                return None
