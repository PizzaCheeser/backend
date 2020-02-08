import requests
import json
from elasticsearch import Elasticsearch
from app import app
import time
import unicodedata

# TODO: finish logs
# TODO: do exceptions
# TODO: merge pizzas with pizzerias in search function
# TODO: pizza -> pizzas, refactor pizzerias_id name


class ES_config():
    def __init__(self, host=app.config['HOST'],
                 pizzerias_id=app.config['ES_PIZZERIAS_ID'],
                 port=app.config['ES_PORT'],
                 location=app.config['ES_LOCATION_ID'],
                 ):
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
            app.logger.info("Succesfully removed database")
        else:
            app.logger.info(f"Failed to remove database: status code: {r.status_code}, {r.text}")


class ES_pizzerias():

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
            app.logger.info("Succesfully created database")
        else:
            app.logger.error(f"Error during database creation, status code: {r.status_code}, {r.text}")

    def delete_index(self):
        r = requests.delete(
            url=self.url + f'{self.pizzerias_id}'
        )

        if r.status_code == 200:
            app.logger.info("Succesfully removed pizzerias index")
        else:
            app.logger.info(f"Failed to remove pizzerias index: status code: {r.status_code}, {r.text}")

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
            app.logger.info(f"Succesfully inserted pizzeria {pizzeria_id}")
        else:
            app.logger.info(f"Failed to insert pizzeria {pizzeria_id}: status code: {r.status_code}, {r.text}")

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
            app.logger.info(f"Pizza {pizza['name']} was added")
            return True
        else:
            app.logger.info(f"Pizza {pizza['name']} wasn't added")
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
            app.logger.info(f"Not updated {pizzeria_id} with postcode {postcode}")

    def recently_retrieved(self, pizzeria_id):
        #TODO: implement this!
        return True


class ES_locations():

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
            app.logger.info(f"Succesfully inserted location {city}, {code}")
        else:
            app.logger.info(f"Failed to insert location {city}, {code}: status code: {r.status_code}, {r.text}")

    def delete_index(self):
        r = self.session.delete(
            url=self.url + f'{self.index}'
        )

        if r.status_code == 200:
            app.logger.info("Succesfully removed locations index")
        else:
            app.logger.info(f"Failed to remove locations index: status code: {r.status_code}, {r.text}")

    def get_location(self, empty=False, city=None, postcode=None):
        query = [
            {"match": {"empty": empty}}
        ]

        if city:
            query.append({"match":{"city":city}})
        if postcode:
            query.append({"match":{"post-code.keyword": postcode}})

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
