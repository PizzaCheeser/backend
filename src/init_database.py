from app.database.base import ES_config
import os

HOST = os.environ.get('HOST')
PIZZERIA_ID = os.environ.get('ES_PIZZERIAS_ID')
ES_PORT = os.environ.get('ES_PORT')
ES_LOCATION_ID = os.environ.get('ES_LOCATION_ID')

database = ES_config(HOST, PIZZERIA_ID, ES_PORT, ES_LOCATION_ID)
database.delete_whole_database()
database.create_structure()