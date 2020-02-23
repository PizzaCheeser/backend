import json

from flask import request, Response

from app.app import app
from app.database.search import ES_search
from app.database.base import ES_config


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
        return Response(headers={"Access-Control-Allow-Origin": '*'}, response=json.dumps(result), status=200)

