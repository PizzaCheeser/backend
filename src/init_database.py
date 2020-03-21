import argparse
import os

from app.database.base import EsConfig

ES_PORT = os.environ.get("ES_PORT", 9200)
ES_PIZZERIAS_ID = os.environ.get("ES_PIZZERIAS_ID", "pizzerias2")
ES_LOCATION_ID = os.environ.get("ES_LOCATION_ID", "locations2")
HOST = os.environ.get("HOST", "elasticsearch")

database = EsConfig(HOST, ES_PIZZERIAS_ID, ES_PORT, ES_LOCATION_ID)

parser = argparse.ArgumentParser()
parser.add_argument('--remove', action='store_true', help='If you want to remove whole database first, add --remove')
args = parser.parse_args()

if args.remove:
    database.delete_whole_database()

database.create_structure()
