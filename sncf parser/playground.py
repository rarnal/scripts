import sqlite3
import pandas as pd
import CONSTANTS


class playground:
    def __init__(self):
        self.conn = sqlite3.connect(CONSTANTS.DATABASE)
    

    def sort_by_cheapest(self):
        request = """
            SELECT
                t1.departure_city,
                t1.departure_station,
                t1.arrival_city,
                t1.arrival_station,
                t1.price + t2.price as price,
                t1.departure_date as 'Depart Date',
                t1.departure_time as 'Depart Time',
                t2.departure_date as 'Return Date',
                t2.departure_time as 'Return Time',
                t1.duration as 'Duration'
            FROM
                trains as t1
                JOIN
                    trains as t2
                    ON t1.arrival_city = t2.departure_city
                    AND Strftime('%Y%m%d', t2.departure_date) - Strftime('%Y%m%d', t1.departure_date) > 0
                    AND Strftime('%Y%m%d', t2.departure_date) - Strftime('%Y%m%d', t1.departure_date) < 4
            WHERE
                t1.departure_city = "Paris"
            ORDER BY
                "Depart Date", price
        """


        res = pd.read_sql_query(request, self.conn)
        print(res)




def main():
    pg = playground()
    pg.sort_by_cheapest()


if __name__=="__main__":
    main()