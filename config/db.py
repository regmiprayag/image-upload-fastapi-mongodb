from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/note"

conn = MongoClient(MONGO_URI)