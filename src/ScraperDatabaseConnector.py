import argparse
import time

import sentry_sdk
from requests.exceptions import TooManyRedirects

from app.app import app
from app.database.base import EsConfig, EsLocations, EsPizzerias
from app.database.search import EsSearch
from app.exceptions.scraperExceptions import UnexpectedWebsiteResponse
from app.scrapers.base_scraper import ScraperBase
from app.scrapers.location import LocationScraper
from app.scrapers.restaurants import PizzeriasScraper
from app.utility.validator import Validator
from config import SENTRY_DSN


class ScraperDatabaseConnector:
    def __init__(self):
        es_settings = EsConfig()
        scraper_settings = ScraperBase()

        self.location = EsLocations(es_settings)
        self.location_scraper = LocationScraper(scraper_settings)
        self.restaurantScraper = PizzeriasScraper(scraper_settings)
        self.pizzerias = EsPizzerias(es_settings)
        self.search = EsSearch(es_settings)
        self.validator = Validator()
        self.MIN_DELAY = int(app.config['MIN_DELAY_BETWEEN_SCRAPING'])

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
                try:
                    self.scrape_locations(self.location_scraper.url + link[1:])
                except Exception as err:
                    app.logger.error(f"Failed to scrape location url=\"{link}\". Err=\"{err}\"")
                    with sentry_sdk.push_scope() as scope:
                        scope.set_extra("url", link)
                        sentry_sdk.capture_exception(err)

    def main(self, city=None):
        '''
        Go through all locations with restaurants and scrape all pizzerias,
        If the pizzeria is already in the database and was scraped recently, it only updates delivery postcode filed
        otherwise it scrapes pizzeria website and inserts pizzeria wit all validated pizzas to the database
        '''
        locations_list = self.location.get_location(city=city, empty=False)
        for location in locations_list:
            with sentry_sdk.push_scope() as scope:
                scope.set_extra("location", location)
                try:
                    all_pizzerias = self.restaurantScraper.get_all_pizzerias(location['link'])
                    for pizzeria in all_pizzerias:
                        self.scrape_pizzeria(location, pizzeria)
                except Exception as err:
                    app.logger.error(f"Failed fetch pizzerias from location=\"{location}\". Err=\"{err}\"")
                    sentry_sdk.capture_exception(err)

    def scrape_pizzeria(self, location, pizzeria):
        with sentry_sdk.push_scope() as scope:
            scope.set_extra("pizzeria", pizzeria)
            try:
                pizzeria_id = pizzeria['endpoint'].split('/')[-1]
                if self.pizzerias.check_if_exists(pizzeria_id):
                    self.pizzerias.update_postcode(pizzeria_id, location['postcode'])

                    timestamp = self.search.get_pizzeria_timestamp(pizzeria_id)
                    timestamp_now = time.time()
                    self.pizzerias.update_field(pizzeria_id, "timestamp", timestamp_now)

                    delay = timestamp_now - timestamp
                    if delay < self.MIN_DELAY:
                        return
                url = self.restaurantScraper.url + pizzeria['endpoint']
                data = self.restaurantScraper.get_pizzeria_data(
                    pizzeria_id=pizzeria_id,
                    postcode=location['postcode'],
                    city=location['city'],
                    name=pizzeria['restaurant_name']
                )

                self.pizzerias.insert_pizzeria(data)
                for pizza in self.restaurantScraper.get_pizza(url):
                    self.scrape_pizza(location, pizza, pizzeria, pizzeria_id)
            except Exception as err:
                app.logger.error(f"Failed fetch pizzeria=\"{pizzeria}\" in location=\"{location}\". Err=\"{err}\"")
                sentry_sdk.capture_exception(err)

    def scrape_pizza(self, location, pizza, pizzeria, pizzeria_id):
        with sentry_sdk.push_scope() as scope:
            scope.set_extra("pizza", pizza)
            try:
                validated_ingredients = self.validator.pizza_validator(pizza)
                pizza.update({"validated_ingredients": validated_ingredients})
                self.pizzerias.insert_pizza(pizzeria_id, pizza)
            except Exception as err:
                app.logger.error(
                    f"Failed fetch pizza=\"{pizza}\" pizzeria=\"{pizzeria}\" in location=\"{location}\". Err=\"{err}\"")
                sentry_sdk.capture_exception(err)


if __name__ == '__main__':
    app.config.from_object('config')
    connector = ScraperDatabaseConnector()

    parser = argparse.ArgumentParser()
    parser.add_argument('--location', help='If you want to scrape all locations add all, if you want to'
                                           'scrape specific location - add name, if you dont want to scrape locations'
                                           'skip this argument')
    parser.add_argument('--city', help='If you want to scrape all pizzerias add all, if you want to'
                                       'scrape pizzerias only for particular city - add name of this city, if you dont'
                                       'want to scrape pizzerias just skip this argument')
    args = parser.parse_args()

    sentry_sdk.init(dsn=SENTRY_DSN)

    try:
        if args.location == 'all':
            connector.scrape_locations()
        elif args.location:
            connector.scrape_locations(url=f'https://www.pyszne.pl/{args.location}')

        if args.city == 'all':
            connector.main()
        elif args.city:
            connector.main(city=args.city)
    except UnexpectedWebsiteResponse as e:
        sentry_sdk.capture_exception(e)
        app.logger.error(e)
    except TooManyRedirects as e:
        sentry_sdk.capture_exception(e)
        app.logger.error(f"Too many redirects: {e}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        app.logger.error(f"Unknown error occurred: {e}")
