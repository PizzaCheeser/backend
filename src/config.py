import os

DEBUG = True
ES_PORT = os.environ.get("ES_PORT",9200)
ES_PIZZERIAS_ID = os.environ.get("ES_PIZZERIAS_ID", "pizzerias2")
ES_LOCATION_ID = os.environ.get("ES_LOCATION_ID", "locations2")
HOST = os.environ.get("HOST", "elasticsearch")