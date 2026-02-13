from bs4 import BeautifulSoup
from src.Enums.InfoType import InfoType
class InfoExtractor:

    def __init__(self, product_info: dict, soup: BeautifulSoup, json_ld_data: dict|None, extraction_rules:dict):
        self.product_info = product_info
        self.soup = soup
        self.json_ld_data = json_ld_data
        self.extraction_rules = extraction_rules

    def extract_info_and_save_it(self, info_type: InfoType, function_to_use: function) -> None:
        product_type_rules = self.extraction_rules.get(info_type, {})

        for priority in sorted(product_type_rules.keys(), key=lambda x: int(x)):   

            if not info_type in self.product_info:
                info = function_to_use(self.soup, self.json_ld_data, priority, self.extraction_rules)

                if info:

                    if info_type != InfoType.ProductChunk.value:
                        self.product_info[info_type] = info

                    else:
                        self.product_info.update(info)
                        break