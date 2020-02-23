from app.exceptions.exceptions import SearchException


class ES_search:
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
            all_ingredients = [key['key'] for key in res["aggregations"]["all_ingredients"]['all_ingredients']['buckets']]
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

    def search_via_ingredients_postcode(self, wanted, not_acceptable, code):
        '''
        Find all ingredients in the specific location
        '''
        # TODO: merge pizzas with pizzerias in search function to return link to order pizza

        if not wanted:
            wanted = []
        if not not_acceptable:
            not_acceptable = []

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
