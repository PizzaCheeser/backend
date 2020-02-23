import json

from flask import request, Response

from app.app import app
from app.database.search import ES_search
from app.database.base import ES_config


@app.route('/api/all_ingredients', methods=['GET'])
def ingredients():
    es_settings = ES_config()
    search = ES_search(es_settings)

    if request.method == 'GET':
        # TODO: search_all_ingredients should take postcode as parameter and sort by it
        ingredients = search.search_all_ingredients()
        return Response(headers={"Access-Control-Allow-Origin": '*'}, response=json.dumps(ingredients), status=200)


@app.route('/api/choosen-ingredients', methods=['POST'])
def ingredients_choice():
    es_settings = ES_config()
    search = ES_search(es_settings)
    if request.method == 'POST':
        ingredients = request.get_json()
        must = ingredients['must']
        must_not = ingredients['must_not']
        post_code = ingredients["code"]

        result = search.search_via_ingredients_postcode(must, must_not, code=post_code)
        return Response(headers={"Access-Control-Allow-Origin": '*'}, response=json.dumps(result), status=200)

