from src.Controllers.Controller import Controller
from src.Db.Db import Db
query = input("Enter your search (be as specific as possible for better results):")
restrictions = {}
db = Db()
controler = Controller(query, db)
print('Controlador creado')
result = controler.run(restrictions)

print(f"RESULTADDOS:\n{result}")