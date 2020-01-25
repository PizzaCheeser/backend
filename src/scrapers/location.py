from bs4 import BeautifulSoup
import requests
import re
from database.base import location
from app import app
from exceptions.scraperExceptions import UnexpectedWebsiteResponse


class LocationScraper():
    def __init__(self, scraper_config):
        self.url = scraper_config.url
        self.redirection = scraper_config.redirection
        self.scraper_config=scraper_config

    def __no_restaurant(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        no_restaurant=soup.find_all('div', 'norestaurant')
        if no_restaurant:
            return True
        else:
            return False

    def __get_delarea_links(self, url):
        soup = self.scraper_config.get_soup(url)
        delareas = soup.find_all('div', 'delarea')
        delarea_links = [delarea.find('a')['href'] for delarea in delareas]
        return delarea_links

    def __find_details(self, url):
        def create_regexp(search, text):
            regexp = f"(?<={search} = ')(.*)(?=')"
            value = re.findall(regexp, text)
            return value

        script = requests.get(url).text

        empty = self.__no_restaurant(script)
        postcode = create_regexp("AreaId", script)
        city = create_regexp("AreaCity", script)
        city_en = create_regexp("AreaString", script)
        # city_en - we are able to get city name without polish characters not used for now

        if len(postcode) != 1:
            app.logger.warning(f"Unexpected website response for {url}, postcode: {postcode} returns too many results")
        if len(city) != 1:
            app.logger.warning(f"Unexpected website response for {url}, city: {city} returns too many results")

        if not postcode:
            raise UnexpectedWebsiteResponse(f"Website {url} doesn't return correct AreaId value (postcode)")
        if not city:
            raise UnexpectedWebsiteResponse(f"Website {url} doesn't return correct AreaCity value (city)")

        country = self.url.split('.')[-1][:-1]

        result = {
            "postcode": postcode[0],
            "city": city[0],
            "link": url,
            "empty": empty,
            "country": country
        }

        return result

    def scrape_locations(self, url=None):
        if not url:
            url = self.url + self.redirection
        links = self.__get_delarea_links(url)

        if not links:
            details = self.__find_details(url)

            app.logger.info(details)

            location.insert_location(
                code=details['postcode'],
                link=details['link'],
                city=details['city'],
                empty=details['empty']
            )
        else:
            for i in links:
                self.scrape_locations(self.url + i[1:])





