from flask import Flask, request, Response
import logging
from flask_cors import CORS
from database.search import ES_search
from database.base import ES_config
import json
from app.app import app


@app.route('/api/all_ingredients', methods=['GET'])
def ingredients():
    ES_settings = ES_config()
    search = ES_search(ES_settings)

    if request.method == 'GET':
        ingredients = search.search_all_ingredients()

    return Response(headers={"Access-Control-Allow-Origin":'*'}, response=json.dumps(ingredients), status=200 )


@app.route('/api/choosen-ingredients', methods=['POST'])
def ingredients_choice():
    ES_settings = ES_config()
    search = ES_search(ES_settings)
    if request.method == 'POST':
        ingredients = request.get_json()
        must = ingredients['must']
        must_not = ingredients['must_not']
        result = search.search_via_ingredients_postcode(must, must_not, code=None)
        #result = search_via_ingredients(must, must_not)
        return Response(headers={"Access-Control-Allow-Origin": '*'}, response=json.dumps(result), status=200)

