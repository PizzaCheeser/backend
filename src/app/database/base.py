import json
import time
import unicodedata
from typing import Dict

import requests
from elasticsearch import Elasticsearch

from app.app import app

PIZZERIAS_INDEX = "pizzerias"
LOCATIONS_INDEX = "locations"
VERSIONS_INDEX = "versions"


class EsConfig:
    def __init__(self, config: Dict):
        host = config["host"]
        port = config["port"]

        self.url = f"http://{host}:{port}/"
        self.port = port
        self.es = Elasticsearch(f'{host}:{self.port}')
        self.header = {"Content-Type": "application/json"}


class EsPizzerias:
    # TODO: Use Elasticsearch module where possible
    '''
    Class responsible for updating and inserting pizzerias and pizzas data into the database
    '''

    def __init__(self, config):
        self.url = config.url
        self.header = config.header
        self.es = config.es

    def delete_index(self):
        r = requests.delete(self.url + f'{PIZZERIAS_INDEX}')

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
            url=self.url + PIZZERIAS_INDEX + f"/_doc/{pizzeria_id}",
            json=pizzeria,
            headers=self.header
        )
        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Successfully inserted pizzeria {pizzeria_id}")
        else:
            app.logger.error(f"Failed to insert pizzeria {pizzeria_id}: status code: {r.status_code}, {r.text}")

    def insert_pizza(self, pizzeria_id, pizza):
        url = self.url + PIZZERIAS_INDEX + f'/_update/{pizzeria_id}/'
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
        # TODO: this function should be in search class
        r = requests.get(
            url=self.url + PIZZERIAS_INDEX + f"/_doc/{pizzeria_id}",
            headers=self.header
        )

        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Pizzeria {pizzeria_id} exists")
            return True
        else:
            app.logger.info(f"Pizzeria {pizzeria_id} doesn't exists")
            return False

    def update_postcode(self, pizzeria_id, postcode):

        data = {
            "script":
                {
                    "source": "ctx._source.delivery_postcodes.contains(params.delivery_postcodes) ? "
                              "(ctx.op = \"none\") : ctx._source.delivery_postcodes.add(params.delivery_postcodes)",
                    "params": {"delivery_postcodes": postcode}
                }
        }

        r = requests.post(self.url + PIZZERIAS_INDEX + '/_update/' + pizzeria_id,
                          json=data, headers=self.header)

        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Updated {pizzeria_id} with postcode {postcode}")
        else:
            app.logger.warning(f"Not updated {pizzeria_id} with postcode {postcode}")

    def update_field(self, pizzeria_id, field, value):
        data = {
            "doc": {
                field: value
            }
        }

        r = requests.post(self.url + PIZZERIAS_INDEX + '/_update/' + pizzeria_id,
                          json=data, headers=self.header)

        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Updated {pizzeria_id} with {field} {value}")
        else:
            app.logger.warning(f"Not updated {pizzeria_id} with {field} {value}")


class EsLocations:
    '''
    Class responsible for inserting pizzerias locations into the database
    '''

    def __init__(self, config):
        self.url = config.url
        # self.index = config.location_index
        self.header = config.header
        self.es = config.es
        self.session = requests.Session()

    def insert_location(self, code, link, city, empty):
        location = {
            "post-code": code,
            "link": link,
            "city": city,
            "empty": empty,
            "timestamp": time.time()
        }

        normalized = unicodedata. \
            normalize('NFKD', city). \
            encode('ASCII', 'ignore'). \
            decode('utf-8'). \
            lower(). \
            replace('/', '_')
        index = f"{normalized}-{code}"

        r = self.session.post(
            url=self.url + LOCATIONS_INDEX + f"/_doc/{index}",
            data=json.dumps(location),
            headers=self.header
        )
        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Successfully inserted location {city}, {code}")
        else:
            app.logger.error(f"Failed to insert location {city}, {code}: status code: {r.status_code}, {r.text}")

    def get_locations_count(self):
        r = self.session.get(
            url=self.url + LOCATIONS_INDEX + f"/_count",
        )
        r.raise_for_status()
        return r.json()["count"]

    def get_location(self, empty=False, city=None, postcode=None, page=None, size=None):
        if not size:
            size = 100000

        from_ = 0
        if page:
            from_ = (page - 1) * size

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

        results = self.es.search(index=LOCATIONS_INDEX, body=full_query, size=size, from_=from_)
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
