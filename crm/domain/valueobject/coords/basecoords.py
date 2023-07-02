from abc import ABC, abstractmethod
from typing import Tuple


class BaseCoords(ABC):
    @abstractmethod
    def get_coords(self) -> Tuple[float, float]:
        pass
