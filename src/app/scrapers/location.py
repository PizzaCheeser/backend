from bs4 import BeautifulSoup
import re
from app.app import app
from app.exceptions.scraperExceptions import UnexpectedWebsiteResponse
from app.scrapers.base_scraper import retry_if_io_error
from retrying import retry


class LocationScraper:
    def __init__(self, scraper_config):
        self.url = scraper_config.url
        self.redirection = scraper_config.redirection
        self.scraper_config = scraper_config

        self.session = scraper_config.session

    @staticmethod
    def __no_restaurant(text):
        soup = BeautifulSoup(text, 'html.parser')
        no_restaurant = soup.find_all('div', 'norestaurant')
        if no_restaurant:
            return True
        else:
            return False

    def get_delarea_links(self, url):
        soup = self.scraper_config.get_soup(url)
        delareas = soup.find_all('div', 'delarea')
        delarea_links = [delarea.find('a')['href'] for delarea in delareas]
        return delarea_links

    @retry(retry_on_exception=retry_if_io_error)
    def __get_script(self, url):
        script = self.session.get(url)
        return script.text

    def find_details(self, url):
        def create_regexp(search, text):
            regexp = f"(?<={search} = ')(.*)(?=')"
            value = re.findall(regexp, text)
            return value

        script = self.__get_script(url)

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
