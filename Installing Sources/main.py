from pymongo import MongoClient
from dotenv import load_dotenv
import json
import os

load_dotenv()

DB_NAME = os.getenv("CLUSTER_NAME")
USER = os.getenv("ADMIN_DB_USERNAME")
PASSWORD = os.getenv("ADMIN_DB_PASSWORD")
HOST = os.getenv("MONGO_HOST")
MONGO_URI = (
    f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/"
    f"?retryWrites=true&w=majority&appName={DB_NAME}"
)
ROOT_FOLDER = "../data"

if not MONGO_URI or not DB_NAME:
    raise RuntimeError("❌ Faltan variables en el .env")

def get_folders(root):
    return [
        name for name in os.listdir(root)
        if os.path.isdir(os.path.join(root, name))
    ]

if __name__ == "__main__":
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("✅ Conectado a la base de datos")

    for folder in get_folders(ROOT_FOLDER):
        folder_path = os.path.join(ROOT_FOLDER, folder)

        for filename in os.listdir(folder_path):
            if not filename.lower().endswith(".json"):
                continue

            file_path = os.path.join(folder_path, filename)
            base_name = os.path.splitext(filename)[0]

            collection_name = base_name

            with open(file_path, "r", encoding="utf-8") as f:
                collection = json.load(f)
                documents = collection.get(base_name, [])

            if not isinstance(documents, list):
                raise ValueError(f"❌ {file_path} no contiene un array JSON")

            if not documents:
                print(f"⚠️ {collection_name}: vacío")
                continue

            db[collection_name].drop()

            db[collection_name].insert_many(documents, ordered=False)
            print(f"✅ {collection_name}: {len(documents)} documentos")

    print("🔥 Importación completa")
