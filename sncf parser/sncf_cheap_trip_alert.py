import datetime
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import CONSTANTS



### PROGRAM DATA ###

JOURNEYS = (
    {
        'departure': 'Paris',
        'arrival': 'Montpellier',
        'schedules': (('5E', '7AE'),), # digit for week day, MORNING -> M, AFTERNOON -> A, EVENING -> E, DAY -> D
    },
)


START_PERIOD = datetime.date.today()
END_PERIOD = START_PERIOD + datetime.timedelta(days=90)


# https://www.oui.sncf/calendar/FRPAR/FRMPT/20190104/ONE_WAY/2/26-NO_CARD/FRPLY-FRMPL-20190104-20190105-26-NO_CARD-2-6225-false-FR?onlyDirectTrains=false&currency=EUR&lang=fr"
#                               FROM  TO     DATE     TYPE   CLASS        STATIONS    START    END      CARD         



# Register all the trips to keep an eye on


def main():
    browser = webdriver.Firefox()
    database = Database()
    generate_journeys(browser, database)



def generate_journeys(browser, database):
    journeys = []
    date_fetch = datetime.datetime.today()

    for data in JOURNEYS:
        journeys.append(Journey(browser, database, date_fetch))
        journeys[-1].initialize(data)
    return journeys



class Journey:
    def __init__(self, browser, database, date_fetch):
        self.browser = browser
        self.database = database
        self.date_fetch = date_fetch
        

    def initialize(self, data):
        self._validate_data(data)
        self.departure = data['departure']
        self.arrival = data['arrival']
        self.schedules = data['schedules']
        self.trips = []

        self._generate_all_urls()
        self._save_trips()


    def _save_trips(self):
        for trip in self.trips:
            self.database.register_trip(trip, self.date_fetch)


    def _generate_all_urls(self):
        for schedule in self.schedules:
            day_go = int(schedule[0][0])
            day_back = int(schedule[1][0])

            day = START_PERIOD
            trip = []

            while day <= END_PERIOD:
                if day.isoweekday() == day_go:
                    url = self._generate_url_day(True, day)
                    trip = [url, day]
                if day.isoweekday() == day_back and trip: # Trip in case we do not have a train_to already
                    url = self._generate_url_day(False, day)
                    trip += [url, day]

                    # Write the trains information in our csv file and reset the trip variable
                    self.trips.append( Trip(trip, self.browser) )
                    trip = []

                day += datetime.timedelta(days=1)


    def _generate_url_day(self, way, day):
        url = CONSTANTS.ROOT_URL
        if way:
            url += CONSTANTS.CITIES[ self.departure ] + "/" + CONSTANTS.CITIES[ self.arrival ] + "/"
        else:
            url += CONSTANTS.CITIES[ self.arrival ] + "/" + CONSTANTS.CITIES[ self.departure ] + "/"
        url += day.isoformat().replace('-', '') + "/"
        url += "ONE_WAY/2/26-NO_CARD/" + day.isoformat().replace('-', '') + "?lang=fr"
        return url

    
    @staticmethod
    def _validate_data(data):
        if data['departure'] not in CONSTANTS.CITIES:
            raise ValueError(f"The city {data['departure']} is unknown")
        if data['arrival'] not in CONSTANTS.CITIES:
            raise ValueError(f"The city {data['arrival']} is unknown")
        return True



class Trip:
    def __init__(self, trip_data, browser):
        self.url_go = trip_data[0]
        self.date_go = trip_data[1]
        self.url_back = trip_data[2]
        self.date_back = trip_data[3]
        self.trains = {'go': [], 'back': []}
        self.browser = browser

        self._get_trains()


    def _get_trains(self):
        # TRAINS TO GO
        self._request_url(self.url_go)
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        proposals = soup.find_all(class_="proposal")
        for proposal in proposals:
            self.trains['go'].append( Train(proposal) )

        # TRAINS BACK
        self._request_url(self.url_back)
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        proposals = soup.find_all(class_="proposal")
        for proposal in proposals:
            self.trains['back'].append( Train(proposal) )
        

    def _request_url(self, url):
        print(url)
        self.browser.get(url)
        try:
            WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'travel-class')))
        except TimeoutException:
            print("too long")
            self._request_url(url)



class Train:
    def __init__(self, proposal):
        self.proposal = proposal
        self._extract_content()
        
    
    def _extract_content(self):
        self.price = self._extract_price(self.proposal)
        self.departure = self._extract_departure_city(self.proposal)
        self.departure_time = self._convert_time(self._extract_departure_time(self.proposal))
        self.arrival = self._extract_arrival_city(self.proposal)
        self.arrival_time = self._convert_time(self._extract_arrival_time(self.proposal))
        self.duration = self._extract_duration(self.proposal)
        self.travel_class = self._extract_travel_class(self.proposal)
            

    @staticmethod
    def _convert_time(time):
        hour, minute = map(int, time.split('h'))
        return datetime.time(hour=hour, minute=minute)


    def _convert_time(self, time):
        hour, minute = map(int, time.split('h'))
        time = datetime.time(hour=hour, minute=minute)
        return time


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



class Database:
    def __init__(self):
        self.db = CONSTANTS.FILE


    def register_trip(self, trip, date):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        try:
            for train in trip.trains['go']:
                cur.execute(
                    "INSERT INTO trains(date_fetch, departure_city, departure_date, departure_time, arrival_city, duration, price, class) \
                    VALUES(?,?,?,?,?,?,?,?)",
                    (
                        date.isoformat(),
                        train.departure,
                        trip.date_go.isoformat(),
                        train.departure_time.isoformat(),
                        train.arrival,
                        train.duration,
                        train.price,
                        train.travel_class
                    )
                )

            for train in trip.trains['back']:
                cur.execute(
                    "INSERT INTO trains(date_fetch, departure_city, departure_date, departure_time, arrival_city, duration, price, class) \
                    VALUES(?,?,?,?,?,?,?,?)",
                    (
                        date.isoformat(),
                        train.departure,
                        trip.date_back.isoformat(),
                        train.departure_time.isoformat(),
                        train.arrival,
                        train.duration,
                        train.price,
                        train.travel_class
                    )
                )
        except Exception as e:
            conn.close()
            raise Exception(e)
        
        conn.commit()
        conn.close()

        


if __name__ == "__main__":
    main()
    
