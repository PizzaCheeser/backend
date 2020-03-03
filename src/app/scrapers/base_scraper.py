import requests
from bs4 import BeautifulSoup
from retry_requests import retry

class ScraperBase():
    def __init__(self, country='PL'
                 ):
        if country == 'PL':
            self.url='https://www.pyszne.pl/'
            self.redirection='restauracja'
        elif country == 'DE':
            self.url='https://www.lieferando.de/'
            self.redirection='lieferservice'

        self.session = retry(requests.Session(), retries=5, backoff_factor=0.2)

    def get_soup(self, url):
        source = self.session.get(url).text  # we're getting website text
        soup = BeautifulSoup(source, 'html.parser')  # and parse to bs
        return soup
