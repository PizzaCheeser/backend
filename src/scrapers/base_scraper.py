import requests
from scrapers.location import LocationScraper
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


scraper_settings = ScraperBase()
obj = LocationScraper(scraper_settings)
obj.scrape_locations()