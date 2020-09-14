from app.app import app
from app.database.base import LOCATIONS_INDEX, PIZZERIAS_INDEX
from app.database.client import Client
from db.migration import BaseMigration


class Migration(BaseMigration):
    def migrate(self, es: Client):
        self.__create_pizzas_index(es)
        self.__create_locations_index(es)

    def roll_back(self, es: Client):
        es.delete_index(LOCATIONS_INDEX)
        es.delete_index(PIZZERIAS_INDEX)

    @staticmethod
    def __create_pizzas_index(es: Client):
        query = {
            "mappings": {
                "properties": {
                    "pizza": {"type": "nested"},
                }
            }
        }

        es.create_index(PIZZERIAS_INDEX, query)
        app.logger.info("Successfully created pizzas index")

    @staticmethod
    def __create_locations_index(es: Client):
        query = {
            "settings": {
                "index": {
                    "max_result_window": 100000
                }
            }
        }

        es.create_index(LOCATIONS_INDEX, query)
        app.logger.info("Successfully created locations index")
