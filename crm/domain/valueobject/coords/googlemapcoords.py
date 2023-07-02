from typing import Tuple

from crm.domain.valueobject.coords.basecoords import BaseCoords


class GoogleMapCoords(BaseCoords):
    def __init__(self, latitude: float, longitude: float):
        """
        googlemap は 緯度経度(lat, lng) で作成する
        """
        self.latitude = latitude
        self.longitude = longitude

    def get_coords(self) -> Tuple[float, float]:
        """
        :return: latitude, longitude
        """
        return self.latitude, self.longitude
