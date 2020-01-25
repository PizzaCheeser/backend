
class ScraperBase():
    def __init__(self, country='PL'
                 ):
        if country == 'PL':
            self.url='https://www.pyszne.pl/'
            self.redirection='restauracja'
        elif country == 'DE':
            self.url='https://www.lieferando.de/'
            self.redirection='lieferservice'
