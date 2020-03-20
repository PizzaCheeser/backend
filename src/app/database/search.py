from app.exceptions.exceptions import SearchException, UnexpectedResult


class EsSearch:
    '''
    Class responsible for searching in the database
    '''

    def __init__(self, config):
        self.url = config.url
        self.pizzerias_id = config.pizzerias_id
        self.header = {"Content-Type": "application/json"}
        self.es = config.es

    def get_all_pizzerias(self):

        try:
            all_results = self.es.search(index=self.pizzerias_id)
        except Exception as e:
            raise SearchException("Get all pizzerias failed") from e

        hits = all_results['hits']['hits']
        return hits

    def search_ingredients_from_location(self, postcode):

        query1 = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                            "delivery_postcodes.keyword": postcode
                        }
                    }
                }
            },
            "aggs": {
                "all_ingredients": {
                    "nested": {
                        "path": "pizza",
                    },

                    "aggs": {
                        "all_ingredients": {"terms": {
                            "field": "pizza.validated_ingredients.keyword",
                            "size": 2147483647,
                        },
                        },
                    }
                },

            }
        }

        try:
            res = self.es.search(
                index=self.pizzerias_id,
                body=query1
            )
        except Exception as e:
            raise SearchException("Get all ingredients failed") from e
        try:
            all_ingredients = [key['key'] for key in
                               res["aggregations"]["all_ingredients"]['all_ingredients']['buckets']]
        except Exception as e:
            raise SearchException("Getting all ingredients from query result failed") from e

        return all_ingredients

    def search_all_ingredients(self):
        query = {
            "aggs": {
                "all_ingredients": {

                    "nested": {
                        "path": "pizza"
                    },
                    "aggs": {
                        "all_ingredients": {"terms": {"field": "pizza.validated_ingredients.keyword",
                                                      "size": 2147483647,
                                                      }}
                    }
                },

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
            all_ingredients = [key['key'] for key in
                               res["aggregations"]["all_ingredients"]['all_ingredients']['buckets']]
        except Exception as e:
            raise SearchException("Getting all ingredients from query result failed") from e
        return all_ingredients

    @staticmethod
    def __query_search_via_ingredients(wanted, not_acceptable):
        def query_from_list(l_ingredients):
            query = [
                {'match': {'pizza.validated_ingredients': {"query": x, "fuzziness": "AUTO", "operator": "AND"}}}
                for x in l_ingredients
            ]

            return query

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

    @staticmethod
    def __query_search_via_postcode(code=None):
        if not code:
            return None
        else:
            query = {"match": {"delivery_postcodes.keyword": code}}
        return query

    def __get_pizzeria_details(self, pizzeria_id):
        query = {
            "query": {
                "terms": {
                    "_id": [pizzeria_id]
                }
            }
        }

        result = self.es.search(index="pizzerias", body=query)['hits']['hits']
        return result

    def get_pizzeria_url(self, pizzeria_id):
        results = self.__get_pizzeria_details(pizzeria_id)

        if not results:
            return "Pizzeria with this id doesn't exist"

        if len(results) != 1:
            raise UnexpectedResult("More than one result")

        return results[0]["_source"]["url"]

    def search_via_ingredients_postcode(self, wanted, not_acceptable, code):
        '''
        Find all ingredients in the specific location
        '''

        if not wanted:
            wanted = list()
        if not not_acceptable:
            not_acceptable = list()

        ingredients_query = self.__query_search_via_ingredients(wanted, not_acceptable)
        postcode_query = self.__query_search_via_postcode(code)
        bool_query = dict()
        if ingredients_query:
            bool_query.update({'must': ingredients_query})
        if postcode_query:
            bool_query.update({"filter": postcode_query})

        query = {
            "size": 1010,
            "_source": "false",
            "query": {
                "bool": bool_query
            }
        }

        try:
            result = self.es.search(index="pizzerias", body=query)['hits']['hits']
        except Exception as e:
            raise SearchException("Searching via ingredients and postcode failed") from e

        pizzas_list = list()
        if len(result) > 0:
            for i in result:
                pizzas_list.extend(i['inner_hits']['pizza']['hits']['hits'])
        else:
            # no matching pizzas
            pizzas_list = list()
        return pizzas_list

    def __clean_matched_pizzas(self, results):

        new_results = [
            {
                "pizzeria_id": result["_id"],
                "pizzeria_name": result['_source']['name'],
                "ingredients": result['_source']['ingredients'],
                "url": self.get_pizzeria_url(result['_id']),
                "size_price": result['_source']['size_price']
            } for result in results
        ]

        return new_results

    def match_pizzas(self, wanted, not_acceptable, code):
        matched_pizzas = self.search_via_ingredients_postcode(wanted, not_acceptable, code)
        cleaned_data = self.__clean_matched_pizzas(matched_pizzas)
        return cleaned_data
