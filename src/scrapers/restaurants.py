from scrapers.base_scraper import ScraperBase

restaurants = ['https://www.pyszne.pl/restauracja-legnica-legnica-59-200',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-203',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-204',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-205',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-206',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-208',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-209',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-210',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-211',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-212',
                'https://www.pyszne.pl/restauracja-legnica-legnica-59-217']

from bs4 import BeautifulSoup
import requests
import re
from database.base import location
from app import app
from exceptions.scraperExceptions import UnexpectedWebsiteResponse


class PizzeriasScraper():
    def __init__(self, scraper_config):
        self.url = scraper_config.url
        self.scraper_config=scraper_config

    def __get_restaurant_name(self, soup):
        name = soup.find_all('div', 'restaurant-name')
        if len(name) == 1:
            return name[0].text
        else:
            raise UnexpectedWebsiteResponse("div: restaurant-name doesn't exist")

    def __get_address(self, soup):
        address = soup.find_all('section', 'card-body')
        if len(address) == 1:
            return address[0].text.strip()
        else:
            raise UnexpectedWebsiteResponse("section card-body doesn't exist")

    def __get_opening_hours(self,soup):
        #TODO: refactoring + exceptions
        info = soup.find_all('div', 'info-tab-section')
        result = dict()
        trs=info[0].find('table').find_all("tr")

        for tr in trs:
            td=tr.find_all("td")
            result.update({td[0].text.strip():td[1].text.strip()})

        return result

    def get_all_pizzerias(self, location_url):
        url = location_url
        soup = self.scraper_config.get_soup(url)
        pizzerias_list=list()

        detailswrapper = soup.find_all('div', 'detailswrapper')

        for detail in detailswrapper:
            restaurant_name = detail.find_all('h2', 'restaurantname')
            href = detail.find_all('a', 'restaurantname')
            kitchens = detail.find_all('div', 'kitchens')

            if not href or not kitchens or not restaurant_name:
                continue

            if len(href) > 1:
                app.logger.warning(
                    f"find all hrefs for {url} returned more hrefs than expected {restaurant_name}")
            if len(restaurant_name) > 1:
                app.logger.warning(f"find all restaurantname for {url} returned more restaurant names {restaurant_name}")
            if len(kitchens) > 1:
                app.logger.warning(
                    f"find all kitchens for {url} returned more result then expected {kitchens}")
            if "Pizza" in kitchens[0].text:
                pizzerias_list.append({"restaurant_name":restaurant_name[0].text.strip(), "endpoint":href[0]['href']})

        return pizzerias_list


    def get_pizzeria_data(self, url, postcode, city):
        soup = self.scraper_config.get_soup(url)
        pizzeria_id = url.split('/')[-1]

        pizzeria = {
            "pizzeria_id": pizzeria_id,
            "name": self.__get_restaurant_name(soup),
            "delivery_postcodes": [postcode],
            "opening_hours": self.__get_opening_hours(soup),
            "city": city,
            "address": self.__get_address(soup),
            "url": url,
        }

        print(pizzeria)

    def insert_pizzeria(self):
        # TODO: already have a function for it
        pass

    def get_pizzas(self):
        pass

    def insert_pizzas(self):
        pass





scraper_settings = ScraperBase()
obj = PizzeriasScraper(scraper_settings)

temp_url='https://www.pyszne.pl/dominos-pizza-legnica'
postcode='59-200'
city='Legnica'

obj.get_pizzeria_data(temp_url, postcode, city)
