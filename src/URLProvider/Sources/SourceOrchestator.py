from src.Db import Db
from types import MappingProxyType

class SourceOrchestator:

    def __init__(self, db: Db):
        self.db = db
    
    def get_sources(self) -> list:
        sources = self.db.find_all("Sources")
        source_context = {}

        for source in sources:
            if source.get("IsActive") is False:
                continue
            source = MappingProxyType(source)
            
            nav_rules = [MappingProxyType(rule)
                for rule in
                self.db.find_by_field("NavRules", "AssociatedSource", source["ID"])
                ]
            extraction_rules = [MappingProxyType(rule)
                for rule in
                self.db.find_by_field("ExtractionRules", "AssociatedSource", source["ID"])
                ]
            validation_rules = [MappingProxyType(rule)
                for rule in
                self.db.find_by_field("ValidationRules", "AssociatedSource", source["ID"])
                ]

            source_context[source["ID"]] = {
                "Source": source,
                "NavRules": nav_rules,
                "ExtractionRules": extraction_rules,
                "ValidationRules": validation_rules
            }

        return MappingProxyType(source_context)
