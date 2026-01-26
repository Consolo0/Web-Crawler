from enum import Enum
from .InfoType import InfoType

class InfoCategories(Enum):
    NumberCategory = {
        InfoType.Price,
        InfoType.Stock,
        InfoType.Rating,
    }
