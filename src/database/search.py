from exceptions.exceptions import SearchException


class ES_search():
    def __init__(self, config):
        self.url = config.url
        self.pizzerias_id = config.pizzerias_id
        self.header = {"Content-Type": "application/json"}
        self.es = config.es

    def get_pizzeria(self, name):
        query = {
            "match":{
                "name": "Pizzeria Muzyczna"}

        }

        query = {
                    "query": {
                        "match" : {
                            "name" : {
                                "query" : "Pizzeria Muzyczna"
                            }
                        }
                    }
                }


        pizzeria = self.es.search(index=self.pizzerias_id, body=query)


        hits = pizzeria['hits']['hits']
        print(hits)
        return hits

    def get_all_pizzerias(self):

        try:
            all_results = self.es.search(index=self.pizzerias_id)
        except Exception as e:
            raise SearchException("Get all pizzerias failed") from e

        hits=all_results['hits']['hits']
        return hits

    def search_all_ingredients(self):

        query = {
                "aggs": {
                    "all_ingredients": {
                        "nested": {
                            "path": "pizza"
                        },
                        "aggs": {
                            "all_ingredients": {"terms": {"field": "pizza.ingredients.keyword"}}
                        }
                    }
                }
            }

        try:
            res = self.es.search(
                index=self.pizzerias_id,
                body=query
            )
        except Exception as e:
            raise SearchException("Get all ingredients failed") from e

        try:
            all_ingredients = [key['key'] for key in res["aggregations"]["all_ingredients"]['all_ingredients']['buckets']]
        except Exception as e:
            raise SearchException("Getting all ingredients from query result failed") from e

        return all_ingredients

    def __query_search_via_ingredients(self, wanted, not_acceptable):
        def query_from_list(l_ingredients):
            query = [{'match': {'pizza.ingredients': {"query": x, "fuzziness": "AUTO", "operator": "AND"}}} for x in
                     l_ingredients]
            return query

        if not wanted or not not_acceptable:
            return None

        full_query = {
                        "nested": {
                            "path": "pizza",
                            "query": {
                                "bool": {
                                    "must": query_from_list(wanted),
                                    "must_not": query_from_list(not_acceptable),
                                }
                            },
                            "inner_hits": {
                                "size": 100
                            }
                        }
                    }

        return full_query

    def __query_search_via_postcode(self, code):
        if not code:
            return None
        else:
            query = {"match": {"delivery_postcodes.keyword": code}}
        return query

    def get_pizzas(self, res):
        pizzas_list = list()
        if len(res) > 0:
            for i in res['hits']['hits']:
                pizzas_list.extend(i['inner_hits']['pizza']['hits']['hits'])
        else:
            pizzas_list=list()

        return pizzas_list

    def get_pizzeria_details(self):
        pass

    def search_via_ingredients_postcode(self, wanted, not_acceptable, code):

        ingredients_query=self.__query_search_via_ingredients(wanted, not_acceptable)
        postcode_query=self.__query_search_via_postcode(code)

        bool_query = dict()
        if ingredients_query:
            bool_query.update({'must':ingredients_query})
        if postcode_query:
            bool_query.update({"filter":postcode_query})

        query = {
            "size": 1010,
            #"_source": "false",
            "query": {
                "bool": bool_query
            }
        }

        try:
            res = self.es.search(index="pizzerias", body=query)
        except Exception as e:
            raise SearchException("Searching via ingredients and postcode failed") from e

        return res

from database.base import ES_config
ES_settings = ES_config()
search=ES_search(ES_settings)
search.get_pizzeria(name='asdf')