from database.base import ES_config, ES_locations, ES_pizzerias
from scrapers.location import LocationScraper
from scrapers.base_scraper import ScraperBase
from scrapers.restaurants import PizzeriasScraper


class ScraperDatabaseConnector():
    def __init__(self):
        ES_settings = ES_config()
        scraper_settings = ScraperBase()

        self.location = ES_locations(ES_settings)
        self.locscraperobj=LocationScraper(scraper_settings)
        self.restaurantScraper = PizzeriasScraper(scraper_settings)
        self.pizzerias = ES_pizzerias(ES_settings)

    def scrape_locations(self, url=None):
        if not url:
            url = self.locscraperobj.url + self.locscraperobj.redirection
        links = self.locscraperobj.get_delarea_links(url)
        # TODO: implement celery
        if not links:
            details = self.locscraperobj.find_details(url)

            #app.logger.info(details)

            self.location.insert_location(
                code=details['postcode'],
                link=details['link'],
                city=details['city'],
                empty=details['empty']
            )
        else:
            for i in links:
                self.scrape_locations(self.locscraperobj.url + i[1:])

    def main(self):
        locations_list = self.location.get_location(city="Wrocław", empty=False)
        print("1")
        for loc in locations_list:
            print("2")
            all_pizzerias = self.restaurantScraper.get_all_pizzerias(loc['link'])
            for pizzeria in all_pizzerias:
                pizzeria_id = pizzeria['endpoint'].split('/')[-1]
                if self.pizzerias.check_if_exists(pizzeria_id):
                    self.pizzerias.update_postcode(pizzeria_id, loc['postcode'])
                    if not self.pizzerias.recently_retrieved(pizzeria_id):
                        continue
                data = self.restaurantScraper.get_pizzeria_data(
                    url=self.restaurantScraper.url + pizzeria['endpoint'],  # TODO: pizzeria_id should be passed here
                    postcode=loc['postcode'],
                    city=loc['city'],
                    name=pizzeria['restaurant_name']
                )
                pizzas_list = self.restaurantScraper.get_pizzas(
                    url=self.restaurantScraper.url + pizzeria['endpoint']
                )

                self.pizzerias.insert_pizzeria(data, pizzas_list)

                for pizza in self.restaurantScraper.get_pizza1(self.restaurantScraper.url + pizzeria['endpoint']):
                    print("PIZZA:", pizza)
                    self.pizzerias.insert_pizza2(pizzeria_id, pizza)




connector = ScraperDatabaseConnector()
#connector.scrape_locations()
connector.main()

#connector.restaurantScraper.get_pizzas(url='https://www.pyszne.pl//pizzeria-roma-kollataja')

