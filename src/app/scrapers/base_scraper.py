import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from retrying import retry
from urllib3.util.retry import Retry


def retry_if_io_error(exception):
    """Return True if we should retry (in this case when it's an IOError), False otherwise"""
    return isinstance(exception, requests.exceptions.ChunkedEncodingError)


class ScraperBase:
    def __init__(self, country='PL'):
        if country == 'PL':
            self.url = 'https://www.pyszne.pl/'
            self.redirection = 'restauracja'
            self.currency = 'PLN'
        elif country == 'DE':
            self.url = 'https://www.lieferando.de/'
            self.redirection = 'lieferservice'
            self.currency = 'EUR'

        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=10,
                                                                     method_whitelist=False)))

        self.session.mount('http://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=10,
                                                                    method_whitelist=False)))

    @retry(retry_on_exception=retry_if_io_error)
    def get_soup(self, url):
        source = self.session.get(url, verify=True).text  # we're getting website text
        soup = BeautifulSoup(source, 'html.parser')  # and parse to bs
        return soup
