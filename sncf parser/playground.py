import sqlite3
import pandas as pd
import re
import datetime
import CONSTANTS
import collections


def get_time(t):
    hour, minute = map(int, t.split('h'))
    return datetime.time(hour=hour, minute=minute)


class playground:
    def __init__(self):
        self.conn = sqlite3.connect(CONSTANTS.DATABASE)
    

    def get_cheapest_per_day(self, depart, arrival, max_price=500, emails=None, low_cost=False, departure_time="00h00", arrival_time="00h00"):

        assert depart in CONSTANTS.CITIES
        assert arrival in CONSTANTS.CITIES
        assert isinstance(max_price, int)
        assert check_emails_provided(emails) or emails == None
        
        time_depart = get_time(departure_time)
        time_arrival = get_time(arrival_time)

        if not low_cost:
            low_costs = (
                "Marne-La-Vallée - Chessy - Gare Tgv et OuiGo (À 200m Du Parc Disneyland Paris)",
                "Montpellier Sud-de-France (à 6 km du centre-ville)",
                "Aeroport Cdg2 Tgv Roissy"
            )
        else:
            low_costs = ()

        max_date = pd.read_sql_query("SELECT MAX(date_fetch) FROM trains", self.conn).iat[0,0]

        request = f"""
            SELECT
                t1.departure_station as Departure,
                t1.arrival_station as Arrival,
                MIN(t1.price + t2.price) as Total_price,
                t1.departure_date as Depart_date,
                t1.departure_time as Depart_time,
                t2.departure_date as Return_date,
                t2.departure_time as Return_time,
                t1.duration as Duration
            FROM
                trains as t1
                JOIN
                    trains as t2
                    ON t1.arrival_city = t2.departure_city
            WHERE
                t1.departure_city = "{depart}"
                AND t1.arrival_city = "{arrival}"
                AND t1.price + t2.price < {max_price}
                AND Strftime('%Y%m%d', t2.departure_date) - Strftime('%Y%m%d', t1.departure_date) > 0
                AND Strftime('%Y%m%d', t2.departure_date) - Strftime('%Y%m%d', t1.departure_date) < 7
                AND t1.date_fetch = "{max_date}"
                AND t2.date_fetch = "{max_date}"
                AND t1.departure_station NOT IN {low_costs}
                AND t1.arrival_station NOT IN {low_costs}
                AND t2.departure_station NOT IN {low_costs}
                AND t2.arrival_station NOT IN {low_costs}
                AND t1.departure_time > "{time_depart}"
                AND t2.departure_time > "{time_arrival}"
            GROUP BY
                t1.id, Depart_date, Return_date
            ORDER BY
                total_price, Depart_date
            
        """

        res = pd.read_sql_query(request, self.conn)
        return res



def check_emails_provided(emails):
    if isinstance(emails, (tuple, list)):
        return all(validate_email(email) for email in email)
    else:
        return validate_email(emails)


def validate_email(email):
    if isinstance(email, str):
        return re.match("^[a-zA-Z0-9.]+\@[a-zA-Z.]+\.[a-zA-Z]{2,3}$", email)
    return False


def draft_email():
    pg = playground()

    for journey in CONSTANTS.JOURNEYS:
        res = pg.get_cheapest_per_day( 
            journey['departure'],
            journey['arrival'],
            max_price=journey['max_price'],
            departure_time=journey['time_depart'],
            arrival_time=journey['time_arrival']
            )

        print(res)


if __name__=="__main__":
    draft_email()