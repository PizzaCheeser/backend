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
                 port=app.config['ES_PORT']
                 ):
        self.url = f"http://{host}:{port}/"
        self.port = port
        self.pizzerias_id = pizzerias_id
        self.es = Elasticsearch(f'{host}:{self.port}')


class ES_pizzerias():

    def __init__(self, config):
        self.url = config.url
        self.pizzerias_id = config.pizzerias_id
        self.header = {"Content-Type": "application/json"}

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

    def delete_database(self):
        r = requests.delete(
            url=self.url + '*'
        )

        if r.status_code == 200:
            app.logger.info("Succesfully removed database")
        else:
            app.logger.info(f"Failed to remove database: status code: {r.status_code}, {r.text}")

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
