from pymongo import MongoClient
from config.settings import settings


client = MongoClient(settings.MONGODB_URI)

db = client[settings.MONGODB_DATABASE]

documents_collection = db["documents"]
unanswered_questions_collection = db["unanswered_questions"]