from typing import Tuple

from crm.domain.valueobject.coords.basecoords import BaseCoords
from crm.domain.valueobject.coords.googlemapcoords import GoogleMapCoords


class CaptureLocationCoords(BaseCoords):
    def __init__(self, longitude: float, latitude: float):
        """
        撮影座標 は 経度緯度(lng, lat) で作成する
        """
        self.longitude = longitude
        self.latitude = latitude

    def get_coords(self) -> Tuple[float, float]:
        """
        :return: longitude, latitude
        """
        return self.longitude, self.latitude

    def to_googlemapcoords(self) -> GoogleMapCoords:
        return GoogleMapCoords(self.latitude, self.longitude)
