from fuzzywuzzy import fuzz

from app.database.base import EsConfig
from app.database.search import EsSearch


class Validator:
    def __init__(self):
        es_settings = EsConfig()
        self.search = EsSearch(es_settings)

    @staticmethod
    def improved_fuzzy(first_ing, scnd_ing):
        # TODO: this should be keept in the database

        if first_ing in ["z boczkiem", "boczek", "boczkiem"] and scnd_ing in ["z boczkiem", "boczek", "boczkiem"]:
            ratio = 100
        if first_ing in ["czerwona cebula", "cebula czerwona"] and scnd_ing in ["czerwona cebula", "cebula czerwona"]:
            ratio = 100
        if first_ing in ["jajka", "jajkiem"] and scnd_ing in ["jajka", "jajkiem"]:
            ratio = 100
        else:
            ratio = fuzz.ratio(first_ing, scnd_ing)

        ratio_str = 'Ratio: {}, first ingredient: {}, scnd ingredient: {} \n'.format(ratio, first_ing, scnd_ing)
        with open("ingredients_ratio.txt", "a") as myfile:
            myfile.write(ratio_str)
        return ratio

    def check_fuzzy(self, pizza_ingredient, all_ingredients_list):
        if pizza_ingredient not in all_ingredients_list:
            simillar_choices = list(
                set([pizza_ingredient if self.improved_fuzzy(pizza_ingredient, ingredient_from_all) < 73
                     else ingredient_from_all for ingredient_from_all in all_ingredients_list]))
            if len(simillar_choices) < 2:
                return pizza_ingredient
            else:
                simillar_choices.pop(simillar_choices.index(pizza_ingredient))
                simillar_choices.sort()
                return simillar_choices[0]
        else:
            return pizza_ingredient

    def pizza_validator(self, pizza):
        all_ingredients = self.search.search_all_ingredients()

        pizza_orginal_ingredients = pizza['ingredients']
        list_orginal_ingredients = pizza_orginal_ingredients.replace(
            ' oraz ', ','
        ).replace(' i ', ',').replace('z ', '').lower().split(',')
        ingredients_list = [word.strip() for word in list_orginal_ingredients]
        validated_ingredients = list()

        for ingredient in ingredients_list:
            if "sos" in ingredient or len(ingredient.split()) > 2:
                pass
            else:
                fuzzied_ingredient = self.check_fuzzy(ingredient, all_ingredients)
                validated_ingredients.append(fuzzied_ingredient)
        return validated_ingredients
