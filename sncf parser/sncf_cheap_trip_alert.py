import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from CONSTANTS import *


JOURNEYS = (
    {
        'departure': 'Paris',
        'arrival': 'Montpellier',
        'schedules': (('5E', '7AE'),), # digit for week day, MORNING -> M, AFTERNOON -> A, EVENING -> E, DAY -> D
    },
)

# https://www.oui.sncf/calendar/FRPAR/FRMPT/20190104/ONE_WAY/2/26-NO_CARD/FRPLY-FRMPL-20190104-20190105-26-NO_CARD-2-6225-false-FR?onlyDirectTrains=false&currency=EUR&lang=fr"
#                               FROM  TO     DATE     TYPE   CLASS        STATIONS    START    END      CARD         



# Register all the trips to keep an eye on


def main():
    browser = webdriver.Firefox()
    journeys = generate_journeys(browser)
    print_journeys(journeys)


def generate_journeys(browser):
    journeys = []
    for data in JOURNEYS:
        journeys.append(Journey(browser))
        journeys[-1].initialize(data)
    return journeys



def print_journeys(journeys, cheapest=True, expensivest=True):

    for journey in journeys:
        if cheapest:
            print("Cheap : ", end = '')
            journey.cheapest.print_trip()
        if expensivest:
            print("Expensive : ", end = '')
            journey.expensivest.print_trip()



class Journey:
    def __init__(self, browser):
        self.browser = browser

        
    def initialize(self, data):
        self._validate_data(data)
        self.departure = data['departure']
        self.arrival = data['arrival']
        self.schedules = data['schedules']
        self.trips = []
        self.cheapest = None
        self.expensivest = None

        self._generate_urls()
    
        

    @staticmethod
    def _validate_data(data):
        if data['departure'] not in CITIES:
            raise ValueError(f"The city {data['departure']} is unknown")
        if data['arrival'] not in CITIES:
            raise ValueError(f"The city {data['arrival']} is unknown")
        return True


    def _generate_urls(self):
        today = datetime.date.today()
        for schedule in self.schedules:
            day_go = int(schedule[0][0])
            day_back = int(schedule[1][0])

            day = datetime.date.today()
            trip = []

            while day-today < datetime.timedelta(days=90):
                if day.isoweekday() == day_go:
                    url = self._generate_url_from_to(True, day)
                    trip.append( Train(url, day, self.browser) )
                if day.isoweekday() == day_back and trip: # Trip in case we do not have a train_to already
                    url = self._generate_url_from_to(False, day)
                    trip.append( Train(url, day, self.browser) )

                    # Register the trains and reset the trip variable
                    if len(trip) == 2:
                        self.trips.append( Trip(trip[0], trip[1]) )
                        self._compare_trip(self.trips[-1])
                        trip = []

                day += datetime.timedelta(days=1)


    def _generate_url_from_to(self, way, day):
        url = ROOT_URL
        if way:
            url += CITIES[ self.departure ] + "/" + CITIES[ self.arrival ] + "/"
        else:
            url += CITIES[ self.arrival ] + "/" + CITIES[ self.departure ] + "/"
        url += day.isoformat().replace('-', '') + "/"
        url += "ONE_WAY/2/26-NO_CARD/" + day.isoformat().replace('-', '') + "?lang=fr"
        return url


    def _compare_trip(self, trip):
        if not self.cheapest or self.cheapest.price > trip.price:
            self.cheapest = trip
        if not self.expensivest or self.expensivest.price < trip.price:
            self.expensivest = trip 




class Trip:
    def __init__(self, train_to, train_back):
        self.train_to = train_to
        self.train_back = train_back
        self._calculate_price()


    def _calculate_price(self):
        self.price = self.train_to.price + self.train_back.price


    def print_trip(self):
        print(f"{self.train_to.departure} / {self.train_back.departure} -> {self.price}€ (from {self.train_to.departure_time} to {self.train_back.departure_time}")



class Train:
    def __init__(self, url, day, browser):
        self.url = url
        self.day = day
        self.browser = browser
        self._request_url()
        self._extract_content()

        

    
    def _request_url(self):
        print(self.url)
        self.browser.get(self.url)
        try:
            WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'travel-class')))
        except TimeoutException:
            print("too long")
            self._request_url()
        self.content = self.browser.page_source

        

    def _extract_content(self):
        soup = BeautifulSoup(self.content, 'html.parser')

        proposals = soup.find_all(class_="proposal")
        for proposal in proposals:
            self.price = self._extract_price(proposal)
            self.departure = self._extract_departure_city(proposal)
            self.departure_time = self._convert_day(self._extract_departure_time(proposal))
            self.arrival = self._extract_arrival_city(proposal)
            self.arrival_time = self._convert_day(self._extract_arrival_time(proposal))
            self.duration = self._extract_duration(proposal)
            self.travel_class = self._extract_travel_class(proposal)
            

    @staticmethod
    def _convert_time(time):
        hour, minute = map(int, time.split('h'))
        return datetime.time(hour=hour, minute=minute)


    def _convert_day(self, time):
        date = self.day
        hour, minute = map(int, time.split('h'))
        time = datetime.time(hour=hour, minute=minute)
        return datetime.datetime.combine(date, time)


    @staticmethod
    def _extract_travel_class(raw_data):
        travel_class = raw_data.find(class_="travel-class")
        return travel_class.find_all("span")[1].string


    @staticmethod
    def _extract_duration(raw_data):
        return raw_data.find(class_="duration").string


    @staticmethod
    def _extract_arrival_time(raw_data):
        time = raw_data.find(class_="arrival")
        return time.find(class_="hour").string


    @staticmethod
    def _extract_arrival_city(raw_data):
        city = raw_data.find(class_="arrival")
        return city.find(class_="station").string


    @staticmethod
    def _extract_departure_time(raw_data):
        time = raw_data.find(class_="departure")
        return time.find(class_="hour").string


    @staticmethod
    def _extract_departure_city(raw_data):
        city = raw_data.find(class_="departure")
        return city.find(class_="station").string


    @staticmethod
    def _extract_price(raw_data):
        price = raw_data.find(class_="price")
        price.span.extract()
        price = price.string
        return int(price)




if __name__ == "__main__":
    main()
    
