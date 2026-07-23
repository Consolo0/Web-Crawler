from pymongo import MongoClient
from dotenv import load_dotenv
import os
from dataclasses import is_dataclass, asdict
from src.Error.MissingData import MissingData
from src.Error.NotExpectedType import NotExpectedType

class Db:
    def __init__(self):
        self.db = self.connect()

    def connect(self):
        load_dotenv()

        DB_NAME = os.getenv("CLUSTER_NAME")
        USER = os.getenv("ADMIN_DB_USERNAME")
        PASSWORD = os.getenv("ADMIN_DB_PASSWORD")
        HOST = os.getenv("MONGO_HOST")

        if not all([DB_NAME, USER, PASSWORD, HOST]):
            raise MissingData("Faltan variables de entorno esenciales en el archivo .env: \n" \
            f"CLUSTER_NAME= {DB_NAME} \
            ADMIN_DB_USERNAME={USER} \
            ADMIN_DB_PASSWORD={PASSWORD} \
            MONGO_HOST={HOST}"
            )
        
        MONGO_URI = (
            f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/"
            f"?retryWrites=true&w=majority&appName={DB_NAME}"
        )

        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        return db

    def find_all(self, collection_name: str) -> list:
        collection = self.db[collection_name]
        documents = list(collection.find())
        return documents
    
    def find_by_field(self, collection_name: str, field: str, value):
        collection = self.db[collection_name]
        result = list(collection.find({field: value}))
        return result
    
    def save(self, data, collection_name=None):
        if not is_dataclass(data):
            raise NotExpectedType("dataclass", type(data), "Data must be an instance of a class")

        collection = self.db[collection_name] if collection_name else self.db[data.__class__.__name__]
        document = asdict(data)
        result = collection.insert_one(document)

        return collection, result.inserted_id
