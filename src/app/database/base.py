import requests
import json
import time
import unicodedata

from app.app import app
from elasticsearch import Elasticsearch


class ES_config:
    def __init__(self, host=None,
                 pizzerias_id=None,
                 port=None,
                 location=None
                 ):
        if not host:
            host = app.config['HOST']
        if not pizzerias_id:
            pizzerias_id = app.config['ES_PIZZERIAS_ID']
        if not port:
            port = app.config['ES_PORT']
        if not location:
            location = app.config['ES_LOCATION_ID']

        self.url = f"http://{host}:{port}/"
        self.port = port
        self.pizzerias_id = pizzerias_id
        self.location_index=location
        self.es = Elasticsearch(f'{host}:{self.port}')
        self.header = {"Content-Type": "application/json"}

    def delete_whole_database(self):
        r = requests.delete(
            url=self.url + '*'
        )

        if r.status_code == 200:
            app.logger.info("Successfully removed database")
        else:
            app.logger.error(f"Failed to remove database: status code: {r.status_code}, {r.text}")


class ES_pizzerias:
    '''
    Class responsible for updating and inserting pizzerias and pizzas data into the database
    '''

    def __init__(self, config):
        self.url = config.url
        self.pizzerias_id = config.pizzerias_id
        self.header = config.header
        self.es = config.es

    def create_structure(self):

        query = {
            "mappings": {
                "properties": {
                    "pizza": {"type": "nested"},
                }
            }
        }

        r = requests.put(
            url=self.url + self.pizzerias_id,
            json=query
        )

        if r.status_code == 200:
            app.logger.info("Successfully created database")
        else:
            app.logger.error(f"Error during database creation, status code: {r.status_code}, {r.text}")

    def delete_index(self):
        r = requests.delete(
            url=self.url + f'{self.pizzerias_id}'
        )

        if r.status_code == 200:
            app.logger.info("Successfully removed pizzerias index")
        else:
            app.logger.error(f"Failed to remove pizzerias index: status code: {r.status_code}, {r.text}")

    def insert_pizzeria(self, data):

        pizzeria_id = data.pop('pizzeria_id')
        opening_hours = json.dumps(data.pop('opening_hours'))

        pizzeria = {
            "name": "",
            "delivery_postcodes": [],
            "timestamp": time.time(),
            "opening_hours": opening_hours,
            "city": "",
            "address": "",
            "url": "",
            "pizza": []
        }
        pizzeria.update(data)

        r = requests.post(
            url=self.url + self.pizzerias_id + f"/_doc/{pizzeria_id}",
            json=pizzeria,
            headers=self.header
        )
        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Successfully inserted pizzeria {pizzeria_id}")
        else:
            app.logger.error(f"Failed to insert pizzeria {pizzeria_id}: status code: {r.status_code}, {r.text}")

    def insert_pizza(self, pizzeria_id, pizza):

        url = self.url + self.pizzerias_id + f'/_update/{pizzeria_id}/'
        body = {
                  "script": {
                    "source": "ctx._source.pizza.add(params.pizza)",
                    "params": {
                      "pizza": pizza
                    }
                  }
                }

        r = requests.post(
            url=url,
            json=body,
            headers=self.header
        )

        if r.status_code == 200 or r.status_code == 201:
            return True
        else:
            app.logger.warning(f"Pizza {pizza['name']} wasn't added")
            return False

    def check_if_exists(self, pizzeria_id):
        r = requests.get(
            url=self.url + self.pizzerias_id + f"/_doc/{pizzeria_id}",
            headers=self.header
        )

        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Pizzeria {pizzeria_id} exists")
            return True
        else:
            app.logger.info(f"Pizzeria {pizzeria_id} doesn't exists")
            return False

    def update_postcode(self, pizzeria_id, postcode):

        #TODO: how to not update if already exists?

        data = {
            "script":
                {"source": "ctx._source.delivery_postcodes.add(params.delivery_postcodes)",
                "params": {"delivery_postcodes": postcode}
                 }
        }

        r = requests.post(self.url+self.pizzerias_id + '/_update/'+pizzeria_id,
                          json=data, headers=self.header)

        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Updated {pizzeria_id} with postcode {postcode}")
        else:
            app.logger.warrning(f"Not updated {pizzeria_id} with postcode {postcode}")

    def recently_retrieved(self, pizzeria_id):
        #TODO: check pizzeria timestamp
        #TODO: check if the timestamp is older than 1 day
        # if so, return False
        return True


class ES_locations:
    '''
    Class responsible for inserting pizzerias locations into the database
    '''

    def __init__(self, config):
        self.url = config.url
        self.index = config.location_index
        self.header = config.header
        self.es = config.es
        self.session = requests.Session()

    def insert_location(self, code, link, city, empty):
        location = {
            "post-code": code,
            "link": link,
            "city": city,
            "empty": empty,
            "timestamp":time.time()
        }

        without_accents = unicodedata.normalize('NFKD', city).encode('ASCII', 'ignore').decode('utf-8').lower()
        index = f"{without_accents}-{code}"

        r = self.session.post(
            url=self.url + self.index + f"/_doc/{index}",
            data=json.dumps(location),
            headers=self.header
        )
        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Successfully inserted location {city}, {code}")
        else:
            app.logger.error(f"Failed to insert location {city}, {code}: status code: {r.status_code}, {r.text}")

    def delete_index(self):
        r = self.session.delete(
            url=self.url + f'{self.index}'
        )

        if r.status_code == 200:
            app.logger.info("Successfully removed locations index")
        else:
            app.logger.error(f"Failed to remove locations index: status code: {r.status_code}, {r.text}")

    def get_location(self, empty=False, city=None, postcode=None):
        query = [
            {"match": {"empty": empty}}
        ]

        if city:
            query.append({"match": {"city": city}})
        if postcode:
            query.append({"match": {"post-code.keyword": postcode}})

        full_query = {
                "query": {
                    "bool": {
                        "must": query,
                    }
                }
        }

        results = self.es.search(index="locations", body=full_query, size=10000)

        results_amount = results["hits"]["total"]["value"]
        location = [
            {"postcode": result['_source']['post-code'],
                        "city": result['_source']['city'],
                        "link": result['_source']['link']
                        } for result in results['hits']['hits']
        ]

        if results_amount != len(location):
            app.logger.warning(f"Not all results are returned for city: {city}, postcode: {postcode}")

        return location
