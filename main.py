from Controllers import Controller
from Db.Db import Db
query = input("Enter your search (be as specific as possible for better results):")
restrictions = {}
db = Db()
controler = Controller(query, db)
result = controler.run(restrictions)