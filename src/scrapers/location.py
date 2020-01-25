from scrapers.config import ScraperConfig
from bs4 import BeautifulSoup
import requests
import re

class LocationScraper():
    def __init__(self, config):
        self.url = config.url
        self.redirection = config.redirection

    def get_soup(self, url):
        source = requests.get(url).text  # we're getting website text
        soup = BeautifulSoup(source, 'html.parser')  # and parse to bs
        return soup

    def scrape_provinces(self, url):
        # https://www.pyszne.pl/restauracja

        soup=self.get_soup(url)

        provinces = soup.find_all('div', 'delarea')
        provinces_list = [i.find('a')['href'] for i in provinces]

        return provinces_list


    def get_postcode(self,url):

        soup = self.get_soup(url)
        test = soup.find_all('div', 'delarea')
        print("TESTESTEST:", test)


        script=requests.get(url).text
        reg_id = "(?<=AreaId = ')(.*)(?=')"
        reg_city = "(?<=AreaCity = ')(.*)(?=')"
        reg_string = "(?<=AreaString = ')(.*)(?=')"

        postcode = re.findall(reg_id, script)
        city = re.findall(reg_city, script)
        city_en = re.findall(reg_string, script)

        print("postcode:", postcode, "city", city, "city en", city_en, "link:", url)

        #find= script.find("AreaId")
        #print("FINDED:", script[find-10:find+40])


config = ScraperConfig()
obj=LocationScraper(config)
provinces_list=obj.scrape_provinces(obj.url+obj.redirection)

restaurants=list()
for province in provinces_list:
    restaurants.extend(obj.scrape_provinces(obj.url + province[1:]))

postcode=list()
for restaurant in restaurants[:1]:
    postcode.extend(obj.scrape_provinces(obj.url + restaurant[1:]))


for postcod in postcode:
    obj.get_postcode(obj.url+postcod)

#print(postcode)
