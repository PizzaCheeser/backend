import json

from flask import request, Response, jsonify
import xml.etree.ElementTree as ET
from xml.dom import minidom

from app.app import app
from app.database.base import EsConfig, EsLocations
from app.database.search import EsSearch

es_settings = EsConfig(app.config["APP"]["es"])
search = EsSearch(es_settings)


@app.route('/sitemap.xml', methods=['GET'])
def get_sitemap():
    locations = EsLocations(es_settings).get_location()
    urlset = ET.Element('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})

    for location in locations:
        url = ET.SubElement(urlset, 'url')
        ET.SubElement(url, 'loc').text = app.config["APP"]["base_url"]+location['postcode']
        ET.SubElement(url, 'changefreq').text = 'weekly'

    rough_string = ET.tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return Response(response=reparsed.toprettyxml(indent="  "))


@app.route('/api/all-ingredients/<postcode>', methods=['GET'])
def ingredients_by_location(postcode):
    ingredients = search.search_ingredients_from_location(postcode)
    return Response(headers={"Access-Control-Allow-Origin": '*'}, response=json.dumps(ingredients), status=200)


@app.route('/api/get-pizzas', methods=['POST'])
def ingredients_choice():
    ingredients = request.get_json()
    must = ingredients['must']
    must_not = ingredients['must_not']
    post_code = ingredients["code"]

    result = search.match_pizzas(must, must_not, code=post_code)
    return Response(headers={"Access-Control-Allow-Origin": '*'}, response=json.dumps(result), status=200)


@app.route('/slack/get-pizzas', methods=['POST'])
def slack_pizza():
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
        name = result['_source']['name']

        ingredients = result['_source']['ingredients']
        result_string += f'*Pizzeria name:* {restaurant_name} \n *Pizza name*: {name} \n *Ingredients*: {ingredients} \n \n'

    response = {
        "response_type": "in_channel",
        "text": result_string
    }

    return jsonify(response)
