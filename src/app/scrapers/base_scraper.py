import requests
from bs4 import BeautifulSoup
#from retry_requests import retry

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging
from retrying import retry

'''
def retryer(funct):

    retry_on_exceptions = (requests.exceptions.ChunkedEncodingError)
    max_retries = 3
    timeout = 5

    def inner(*args, **kwargs):
        for i in range(max_retries):
            try:
                result = funct(*args, **kwargs)
            except retry_on_exceptions:
                time.sleep(timeout)
                continue
            else:
                return result
        else:
            raise Exception("Unfortunatelly failed again but function works fine")

    return inner()
'''

#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)

def retry_if_io_error(exception):
    """Return True if we should retry (in this case when it's an IOError), False otherwise"""
    return isinstance(exception, requests.exceptions.ChunkedEncodingError)

class ScraperBase():
    def __init__(self, country='PL'
                 ):
        if country == 'PL':
            self.url='https://www.pyszne.pl/'
            self.redirection='restauracja'
        elif country == 'DE':
            self.url='https://www.lieferando.de/'
            self.redirection='lieferservice'

        self.session = requests.Session()
        self.session = retry(requests.Session(), retries=5, connect = 5, backoff_factor=0.2)
        #self.session.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=10,
        #                                                             method_whitelist=False)))

    @retry(retry_on_exception=retry_if_io_error)
    def get_soup(self, url):
        #source = self.session.get('https://www.asdfasdf.psota.pl').text  # we're getting website text
        #source = self.session.get(url, retries=Retry(10)).text  # we're getting website text

        source = self.session.get(url, verify=True).text  # we're getting website text
        '''
        try:
            source = self.session.get(url, verify=True).text  # we're getting website text
            #source = self.session.get('www.asdfasdf.psota.pl').text  # we're getting website text
        except:
            print("ERROR!")
        '''
        #source = source.text
        soup = BeautifulSoup(source, 'html.parser')  # and parse to bs
        return soup
