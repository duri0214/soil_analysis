from abc import abstractmethod


class BasePhoto:
    @abstractmethod
    def _extract_exif_data(self) -> dict:
        pass

    @abstractmethod
    def _extract_date(self) -> str:
        pass

    @abstractmethod
    def _extract_location(self) -> float:
        pass

    @abstractmethod
    def _extract_azimuth(self) -> float:
        pass
