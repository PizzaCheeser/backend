import json

from flask import request, Response, jsonify

from app.app import app
from app.database.search import ES_search
from app.database.base import ES_config


@app.route('/api/all_ingredients_old', methods=['GET'])
def ingredients():
    es_settings = ES_config()
    search = ES_search(es_settings)

    if request.method == 'GET':
        ingredients = search.search_all_ingredients()
        return Response(headers={"Access-Control-Allow-Origin": '*'}, response=json.dumps(ingredients), status=200)


@app.route('/api/all_ingredients/<postcode>', methods=['GET'])
def ingredients_by_location(postcode):
    es_settings = ES_config()
    search = ES_search(es_settings)

    if request.method == 'GET':
        ingredients = search.search_ingredients_from_location(postcode)
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


@app.route('/slack/get-pizzas', methods=['POST'])
def slack_pizza():
    es_settings = ES_config()
    search = ES_search(es_settings)

    if request.method == 'POST':
        params = request.form['text']
        args = params.split(';')
        if len(args) == 3:
            post_code = args[0]
            wanted = [ingredient for ingredient in args[1].split(',') if ingredient]
            not_wanted = [ingredient for ingredient in args[2].split(',') if ingredient]

        else:
            response = {
                "response_type": "in_channel",
                "text": "Please put parameters correctly: `/pizza <post-code>;<wanted>;<not-wanted>`"
            }

            return jsonify(response)

        results = search.search_via_ingredients_postcode(wanted, not_wanted, code=post_code)
        results_number = len(results)

        result_string = f'I found {results_number} dreamed pizza! :) Bon appetit! \n \n'
        for result in results:
            restaurant_name = result['_id']
            name=result['_source']['name']

            ingredients = result['_source']['ingredients']
            result_string += f'*Pizzeria name:* {restaurant_name} \n *Pizza name*: {name} \n *Ingredients*: {ingredients} \n \n'

        response = {
            "response_type": "in_channel",
            "text": result_string
        }

        return jsonify(response)

