import requests
from scrapers.restaurants import PizzeriasScraper
from database.base import ES_config, ES_locations, ES_pizzerias

from bs4 import BeautifulSoup


class ScraperBase():
    def __init__(self, country='PL'
                 ):
        if country == 'PL':
            self.url='https://www.pyszne.pl/'
            self.redirection='restauracja'
        elif country == 'DE':
            self.url='https://www.lieferando.de/'
            self.redirection='lieferservice'

    def get_soup(self, url):
        source = requests.get(url).text  # we're getting website text
        soup = BeautifulSoup(source, 'html.parser')  # and parse to bs
        return soup


#scraper_settings = ScraperBase()
#obj = LocationScraper(scraper_settings)
#obj.scrape_locations()




scraper_settings = ScraperBase()
restaurantScraper = PizzeriasScraper(scraper_settings)

config = ES_config()
location = ES_locations(config)
locations_list = location.get_location(city="Wrocław", empty=False)

pizzerias = ES_pizzerias(config)

#pizzerias.update_postcode('da-grasso-legnica', '95')


for loc in locations_list:
    all_pizzerias = restaurantScraper.get_all_pizzerias(loc['link'])
    for pizzeria in all_pizzerias:
        pizzeria_id = pizzeria['endpoint'].split('/')[-1]
        print(pizzeria)
        if pizzerias.check_if_exists(pizzeria_id):
            pizzerias.update_postcode(pizzeria_id, loc['postcode'])
            if pizzerias.check_timestamp(pizzeria_id):
                continue
        data = restaurantScraper.get_pizzeria_data(
            url=restaurantScraper.url + pizzeria['endpoint'], # TODO: pizzeria_id should be passed here
            postcode=loc['postcode'],
            city=loc['city'],
            name=pizzeria['restaurant_name']
        )

        pizzerias.insert_pizzeria(data)