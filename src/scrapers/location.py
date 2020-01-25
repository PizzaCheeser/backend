from scrapers.base_scraper import ScraperBase
from bs4 import BeautifulSoup
import requests
import re
from database.base import location
import database.base

class LocationScraper():
    def __init__(self, scraper_config):
        self.url = scraper_config.url
        self.redirection = scraper_config.redirection

    def get_soup(self, url):
        source = requests.get(url).text  # we're getting website text
        soup = BeautifulSoup(source, 'html.parser')  # and parse to bs
        return soup

    def __no_restaurant(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        no_restaurant=soup.find_all('div', 'norestaurant')
        if no_restaurant:
            return True
        else:
            return False

    def get_delarea_links(self, url):
        # https://www.pyszne.pl/restauracja
        soup = self.get_soup(url)
        delareas = soup.find_all('div', 'delarea')
        delarea_links = [delarea.find('a')['href'] for delarea in delareas]
        return delarea_links

    def scrape_provinces(self, url):

        links = self.get_delarea_links(url)

        if not links:
            details=self.find_details(url)
            print(details)
            location.insert_location(code=details['postcode'], link=details['link'], city=details['city'], empty=details['empty'])
        else:
            for i in links:
                self.scrape_provinces(obj.url + i[1:])



    def find_details(self,url):

        script=requests.get(url).text
        empty=self.__no_restaurant(script)
        reg_id = "(?<=AreaId = ')(.*)(?=')"
        reg_city = "(?<=AreaCity = ')(.*)(?=')"
        reg_string = "(?<=AreaString = ')(.*)(?=')"

        postcode = re.findall(reg_id, script)
        city = re.findall(reg_city, script)
        city_en = re.findall(reg_string, script)

        result = {"postcode": postcode[0], "city": city[0], "city en": city_en[0], "link": url, "empty": empty}

        return result


    def scrape_locations(self):
        base = self.url + self.redirection
        result =self.scrape_provinces(base)



scraper_settings = ScraperBase()
obj=LocationScraper(scraper_settings)
#provinces_list=obj.scrape_provinces(obj.url+obj.redirection)
obj.scrape_locations()



