import datetime

ROOT_URL = "https://www.oui.sncf/calendar/"
DATABASE = "/home/romain/var/www/html/scripts/sncf parser/database2.db"
PERIOD_LOOKUP_INTERVAL = 90

JOURNEYS = (
    {
        'departure': 'Paris',
        'arrival': 'London',    # Beware that the departure and arrival cities are referenced in CONSTANTS.CITIES
        'schedules': ((5, 7),), # the digits represent a week day (1 being monday and 7 sunday)tuple because we can insert several schedules
                                # Tuple in order to let the possibiliy to have several schedules for a trip - example: ((5, 7), 6, 7))
        'time_depart': "17h00",
        'time_arrival': "16h00",
        'max_price': 150
    },                          
    {
        'departure': 'Paris',
        'arrival': 'Montpellier',
        'schedules': ((5, 7),),
        'time_depart': "17h00",
        'time_arrival': "16h00",
        'max_price': 150
    },
    {
        'departure': 'Paris',
        'arrival': 'Avignon',
        'schedules': ((5, 7),),
        'time_depart': "17h00",
        'time_arrival': "16h00",
        'max_price': 150
    },
)

########## ENGINE DATA #################

STATIONS = {
    'Paris': ("FRPLY",),
    'Montpellier': ("FRMPL",),
}

CITIES = {
    'Paris': "FRPAR",
    'Montpellier': "FRMPT",
    'Avignon': "FRAVN",
    'Brest': "FRBES",
    'Quimper': "FRUIP",
    'Grenoble': "FRGNL",
    'London': "GBLON"
}

SCHEDULES = {
    'M': ( datetime.time(hour=0),  datetime.time(hour=14) ),
    'A': ( datetime.time(hour=14), datetime.time(hour=19) ),
    'E': ( datetime.time(hour=19), datetime.time(hour=23, minute=59) ),
    'D': ( datetime.time(hour=0),  datetime.time(hour=23, minute=59) )
}