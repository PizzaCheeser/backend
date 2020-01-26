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
        info = soup.find_all('div', 'info-tab-section')
        opening_hours = dict()
        if len(info) < 1:
            app.logger.warning("List of information is too short, opening hours not added")
            return opening_hours

        trs = info[0].find('table').find_all("tr")
        if not trs:
            app.logger.warning("List of trs doesn't exist, opening hours not added")
            return opening_hours

        for tr in trs:
            td = tr.find_all("td")
            if len(td) != 2:
                print("asdasdfsafd")

            opening_hours.update({td[0].text.strip():td[1].text.strip()})

        return opening_hours

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


    def get_pizzeria_data(self, url, postcode, city, name):
        soup = self.scraper_config.get_soup(url)
        pizzeria_id = url.split('/')[-1] #TODO: change this

        pizzeria = {
            "pizzeria_id": pizzeria_id,
            "name": name,
            "delivery_postcodes": [postcode],
            "opening_hours": self.__get_opening_hours(soup),
            "city": city,
            "address": self.__get_address(soup),
            "url": url,
        }
        return pizzeria

    def insert_pizzerias(self, loc):
        all_pizzerias = self.get_all_pizzerias(loc['link'])
        for pizzeria in all_pizzerias:
            data = self.get_pizzeria_data(
                    url=self.url+pizzeria['endpoint'],
                    postcode=loc['postcode'],
                    city=loc['city'],
                    name=pizzeria['restaurant_name']
                )
    def get_pizzas(self):
        pass

    def insert_pizzas(self):
        pass




