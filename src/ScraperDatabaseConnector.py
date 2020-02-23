from app.database.search import ES_search
from app.scrapers.location import LocationScraper
from app.scrapers.base_scraper import ScraperBase
from app.scrapers.restaurants import PizzeriasScraper
from app.utility.validator import Validator
from app.database.base import ES_config, ES_locations, ES_pizzerias
from app.app import app


class ScraperDatabaseConnector():
    def __init__(self):
        es_settings = ES_config()
        scraper_settings = ScraperBase()

        self.location = ES_locations(es_settings)
        self.location_scraper = LocationScraper(scraper_settings)
        self.restaurantScraper = PizzeriasScraper(scraper_settings)
        self.pizzerias = ES_pizzerias(es_settings)
        self.search = ES_search(es_settings)
        self.validator = Validator()

    def scrape_locations(self, url=None):
        '''
        Going throught all pages in the page like that: https://www.pyszne.pl/restauracja-krakow
        And searching for all locations with restaurants
        If there is a website with postcode for particular place but there is no available restaurants
        "empty" field is set as True
        '''

        if not url:
            url = self.location_scraper.url + self.location_scraper.redirection
        links = self.location_scraper.get_delarea_links(url)

        if not links:
            details = self.location_scraper.find_details(url)

            self.location.insert_location(
                code=details['postcode'],
                link=details['link'],
                city=details['city'],
                empty=details['empty']
            )
        else:
            for link in links:
                self.scrape_locations(self.location_scraper.url + link[1:])

    def main(self):
        '''
        Go through all locations with restaurants and scrape all pizzerias,
        If the pizzeria is already in the database and was scraped recently, it only updates delivery postcode filed
        otherwise it scrapes pizzeria website and inserts pizzeria wit all validated pizzas to the database
        '''

        locations_list = self.location.get_location(city="Kraków", empty=False)
        for location in locations_list:
            all_pizzerias = self.restaurantScraper.get_all_pizzerias(location['link'])
            for pizzeria in all_pizzerias:
                pizzeria_id = pizzeria['endpoint'].split('/')[-1]
                if self.pizzerias.check_if_exists(pizzeria_id):
                    self.pizzerias.update_postcode(pizzeria_id, location['postcode'])
                    if self.pizzerias.recently_retrieved(pizzeria_id):
                        continue
                url = self.restaurantScraper.url + pizzeria['endpoint']
                data = self.restaurantScraper.get_pizzeria_data(
                    pizzeria_id=pizzeria_id,
                    postcode=location['postcode'],
                    city=location['city'],
                    name=pizzeria['restaurant_name']
                )

                self.pizzerias.insert_pizzeria(data)
                for pizza in self.restaurantScraper.get_pizza(url):
                    validated_ingredients = self.validator.pizza_validator(pizza)
                    pizza.update({"validated_ingredients": validated_ingredients})
                    self.pizzerias.insert_pizza(pizzeria_id, pizza)


if __name__ == '__main__':
    app.config.from_object('config')
    connector = ScraperDatabaseConnector()
    while True:
        connector.scrape_locations(url='https://www.pyszne.pl/restauracja-krakow-krakow-srodmiescie')
        connector.main()
