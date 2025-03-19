from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class NominatimAPI:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="TripAdvisorBot/1.0 (mike@example.com)")  

    def get_coordinates(self, location_name: str):
        """
        Получает координаты (lat, lon) для заданного названия места
        """
        try:
            location = self.geolocator.geocode(location_name, timeout=10)
            if location:
                return location.latitude, location.longitude
            else:
                print(f"[ERROR] Nominatim: Не найдено место '{location_name}'")
                return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"[ERROR] Nominatim: Ошибка сети - {e}")
            return None