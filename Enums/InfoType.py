from enum import Enum
class InfoType(Enum):
    Price = "Price"
    Stock = "Stock"
    Rating = "Rating"
    ProductTitle = "ProductTitle"
    NumberCategory = [Price, Stock, Rating]
