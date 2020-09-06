from fuzzywuzzy import fuzz

from app.app import app
from app.database.base import EsConfig
from app.database.search import EsSearch
import morfeusz2


class Validator:
    def __init__(self):
        es_settings = EsConfig(app.config["APP"]["es"])
        self.search = EsSearch(es_settings)
        self.morfeusz = morfeusz2.Morfeusz()

    def get_basic_form(self, word):
        analysed_list = self.morfeusz.analyse(word)
        for analysed in analysed_list:
            result = analysed[2]
            abbreviation = result[2].split(':')[0]
            if abbreviation == 'subst':
                validated_word = result[1].split(':')[0]
                return validated_word
        return None

    @staticmethod
    def find_existing_ingredient(ingredient, all_ingredients):
        for any_ingredient in all_ingredients:
            fuzz_ratio = fuzz.ratio(any_ingredient, ingredient)
            if fuzz_ratio > 82:
                return any_ingredient
        return ingredient

    def pizza_validator(self, pizza):
        all_ingredients = self.search.search_ingredients()

        list_original_ingredients = pizza['ingredients']. \
            replace(' oraz ', ' ').replace(' i ', ' '). \
            replace('z ', '').replace(',', ' ').lower().split()

        ingredients_list = [word.strip() for word in list_original_ingredients]

        validated_ingredients = set()
        for ingredient in ingredients_list:
            basic_form_ingredient = self.get_basic_form(ingredient)
            if basic_form_ingredient:
                fuzzied_ingredient = self.find_existing_ingredient(basic_form_ingredient, all_ingredients)
                validated_ingredients.add(fuzzied_ingredient)
        return list(validated_ingredients)
