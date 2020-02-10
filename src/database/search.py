from exceptions.exceptions import SearchException


class ES_search():
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
            print("CONFIG:", self.url)
            raise SearchException("Get all ingredients failed") from e
        try:
            all_ingredients = [key['key'] for key in res["aggregations"]["all_ingredients"]['all_ingredients']['buckets']]
        except Exception as e:
            print("CONFIG:", self.url)
            raise SearchException("Getting all ingredients from query result failed") from e
        return all_ingredients

    def __query_search_via_ingredients(self, wanted, not_acceptable):
        print("INGREDIENTS:")
        print(wanted, not_acceptable)
        def query_from_list(l_ingredients):
            query = [{'match': {'pizza.validated_ingredients': {"query": x, "fuzziness": "AUTO", "operator": "AND"}}} for x in
                     l_ingredients]
            return query

        #if not wanted or not not_acceptable:
        #    return None

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

    def __query_search_via_postcode(self, code=None):
        if not code:
            return None
        else:
            query = {"match": {"delivery_postcodes.keyword": code}}
        return query

    '''
    def get_pizzas(self, res):
        pizzas_list = list()
        if len(res) > 0:
            for i in res['hits']['hits']:
                pizzas_list.extend(i['inner_hits']['pizza']['hits']['hits'])
        else:
            pizzas_list=list()

        return pizzas_list
    '''
    def get_pizzeria_details(self):
        pass

    def search_via_ingredients_postcode(self, wanted, not_acceptable, code="30-122"):

        if not wanted:
            wanted = []
        if not not_acceptable:
            not_acceptable = []
        print("QUERYQUERYL")
        print(wanted, not_acceptable, code)
        ingredients_query=self.__query_search_via_ingredients(wanted, not_acceptable)
        postcode_query=self.__query_search_via_postcode(code)
        print("INGREDIENTS QUERY:")
        print(ingredients_query)
        print("POSTCODE QUERY")
        print(postcode_query)

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
        print("QUERY QUERY:")
        print(query)
        try:
            result = self.es.search(index="pizzerias", body=query)['hits']['hits']
        except Exception as e:
            raise SearchException("Searching via ingredients and postcode failed") from e

        #print(result)
        pizzas_list = list()
        if len(result) > 0:
            for i in result:
                print(ingredients_query, postcode_query)
                pizzas_list.extend(i['inner_hits']['pizza']['hits']['hits'])
        else:
            # no matching pizzas
            pizzas_list = list()
        print(pizzas_list)
        return pizzas_list
