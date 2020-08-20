import os

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
ES_PORT = os.environ.get("ES_PORT", 9200)
ES_PIZZERIAS_ID = os.environ.get("ES_PIZZERIAS_ID", "pizzerias2")
ES_LOCATION_ID = os.environ.get("ES_LOCATION_ID", "locations2")
HOST = os.environ.get("HOST", "elasticsearch")

MIN_DELAY_BETWEEN_SCRAPING = os.environ.get("MIN_DELAY_BETWEEN_SCRAPING", 86400)
