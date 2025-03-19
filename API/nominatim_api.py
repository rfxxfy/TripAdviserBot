from geopy.geocoders import Nominatim

class NominatimAPI:
    def __init__(self, user_agent: str = "myGeoBot", timeout: int = 10):
        """
        Инициализируем geolocator из geopy.
        - user_agent: любое произвольное название приложения
        - timeout: время ожидания ответа
        """
        self.geolocator = Nominatim(user_agent=user_agent, timeout=timeout)

    def get_coordinates(self, location_name: str):
        """
        Принимает название города/адреса, возвращает кортеж (lat, lon) или None, если не удалось найти.
        """
        if not location_name:
            return None
        try:
            location = self.geolocator.geocode(location_name)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Nominatim error: {e}")
        return None