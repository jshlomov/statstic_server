import os

from dotenv import load_dotenv

from app import db

load_dotenv(verbose=True)

db_url = os.environ['MONGO_DB_URL']
db_name = os.environ['MONGO_DB_NAME']
collection_name =os.environ['MONGO_DB_ATTACKS_COLLECTION']
collection_test = os.environ['MONGO_DB_ATTACKS_COLLECTION_TEST']
