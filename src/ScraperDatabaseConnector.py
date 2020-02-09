from database.base import ES_config, ES_locations, ES_pizzerias
from database.search import ES_search
from scrapers.location import LocationScraper
from scrapers.base_scraper import ScraperBase
from scrapers.restaurants import PizzeriasScraper
from utility.validator import Validator
from fuzzywuzzy import fuzz


class ScraperDatabaseConnector():
    def __init__(self):
        ES_settings = ES_config()
        scraper_settings = ScraperBase()

        self.location = ES_locations(ES_settings)
        self.location_scraper=LocationScraper(scraper_settings)
        self.restaurantScraper = PizzeriasScraper(scraper_settings)
        self.pizzerias = ES_pizzerias(ES_settings)
        self.search = ES_search(ES_settings)
        self.validator = Validator()




    def scrape_locations(self, url=None):
        if not url:
            url = self.location_scraper.url + self.location_scraper.redirection
        links = self.location_scraper.get_delarea_links(url)
        # TODO: implement celery
        if not links:
            details = self.location_scraper.find_details(url)

            #app.logger.info(details)

            self.location.insert_location(
                code=details['postcode'],
                link=details['link'],
                city=details['city'],
                empty=details['empty']
            )
        else:
            for i in links:
                self.scrape_locations(self.location_scraper.url + i[1:])

    def main(self):
        locations_list = self.location.get_location(city="Kraków", empty=False)
        for loc in locations_list:
            all_pizzerias = self.restaurantScraper.get_all_pizzerias(loc['link'])
            for pizzeria in all_pizzerias:
                pizzeria_id = pizzeria['endpoint'].split('/')[-1]
                if self.pizzerias.check_if_exists(pizzeria_id):
                    self.pizzerias.update_postcode(pizzeria_id, loc['postcode'])
                    if not self.pizzerias.recently_retrieved(pizzeria_id):
                        continue
                url = self.restaurantScraper.url + pizzeria['endpoint']
                data = self.restaurantScraper.get_pizzeria_data(
                    pizzeria_id=pizzeria_id,
                    postcode=loc['postcode'],
                    city=loc['city'],
                    name=pizzeria['restaurant_name']
                )

                self.pizzerias.insert_pizzeria(data)
                for pizza in self.restaurantScraper.get_pizza(url):
                    validated_ingredients = self.validator.pizza_validator(pizza)
                    pizza.update({"validated_ingredients": validated_ingredients})
                    self.pizzerias.insert_pizza(pizzeria_id, pizza)

                    #self.pizzerias.insert_validated(pizzeria_id, pizza, validated_ingredients)




connector = ScraperDatabaseConnector()
#connector.scrape_locations(url='https://www.pyszne.pl/restauracja-krakow-krakow-srodmiescie')
connector.main()
#connector.pizza_validator()

