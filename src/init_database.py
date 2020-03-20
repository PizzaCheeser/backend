from app.database.base import ES_config
import os

ES_PORT = os.environ.get("ES_PORT",9200)
ES_PIZZERIAS_ID = os.environ.get("ES_PIZZERIAS_ID", "pizzerias2")
ES_LOCATION_ID = os.environ.get("ES_LOCATION_ID", "locations2")
HOST = os.environ.get("HOST", "elasticsearch")

database = ES_config(HOST, ES_PIZZERIAS_ID, ES_PORT, ES_LOCATION_ID)
#database.delete_whole_database()
database.create_structure()