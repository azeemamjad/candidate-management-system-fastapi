from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
if client.admin.command("ping"):
    print("connected!")

DB_NAME = "users_db_test" if os.getenv("TESTING") else "users_db"
db = client[DB_NAME]

users_collection = db["users-collection"] # create a colection for user in database
users_collection.create_index("UUID", unique=True) # makingg UUID unique
users_collection.create_index("email", unique=True) # making email Unique


candidates_collection = db["candidates-collection"] # create collection for candidates in database
candidates_collection.create_index("UUID", unique=True) # makingg UUID unique
candidates_collection.create_index("email", unique=True) # making email Unique