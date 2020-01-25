import requests
from flask import Flask
import json
from elasticsearch import Elasticsearch
from app import app
import time

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

    def insert_pizzeria(self, name, **kwargs):
        pizzeria = {
            "name": name,
            "delivery_postcodes": [],
            "scraped_timestamp": time.time(),
            "opening_hours": "",
            "city": "",
            "address": "",
            "url": "",
            "pizza": {}
        }
        pizzeria.update(kwargs)
        r = requests.post(
            url=self.url + self.pizzerias_id + f"/_doc/{name}",
            data=json.dumps(pizzeria),
            headers=self.header
        )
        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Succesfully inserted pizzeria {name}")
        else:
            app.logger.info(f"Failed to insert pizzeria {name}: status code: {r.status_code}, {r.text}")

    def insert_pizza(self, pizzeria_name, pizza_name, **kwargs):

        pizza = {
            "name": pizza_name,
            "ingredients": [],
            "price_size_ratio": {}
        }

        pizza.update(kwargs)

        r = requests.post(
            url=self.url + self.pizzerias_id + f"/_doc/{pizzeria_name}",
            data=json.dumps({"pizza": pizza}),
            headers=self.header
        )

        if r.status_code == 201 or r.status_code == 200:
            app.logger.info(f"Succesfully inserted pizza {pizza_name}")
        else:
            app.logger.info(f"Failed to insert pizza {pizza_name}: status code: {r.status_code}, {r.text}")

import unicodedata

class ES_locations():

    def __init__(self, config):
        self.url = config.url
        self.index = config.location_index
        self.header = config.header

    def insert_location(self, code, link, city):
        location = {
            "post-code": code,
            "link": link,
            "city": city,
        }

        without_accents = unicodedata.normalize('NFKD', city).encode('ASCII', 'ignore').decode('utf-8').lower()
        index = f"{without_accents}-{code}"

        r = requests.post(
            url=self.url + self.index + f"/_doc/{index}",
            data=json.dumps(location),
            headers=self.header
        )
        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"Succesfully inserted location {city}, {code}")
        else:
            app.logger.info(f"Failed to insert location {city}, {code}: status code: {r.status_code}, {r.text}")

    def delete_index(self):
        r = requests.delete(
            url=self.url + f'{self.index}'
        )

        if r.status_code == 200:
            app.logger.info("Succesfully removed locations index")
        else:
            app.logger.info(f"Failed to remove locations index: status code: {r.status_code}, {r.text}")


config = ES_config()
location = ES_locations(config)
location.delete_index()
location.insert_location('30-122', 'https://www.pyszne.pl/restauracja-krakow-krakow-krowodrza-30-122' ,'Kraków')