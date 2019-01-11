import datetime

ROOT_URL = "https://www.oui.sncf/calendar/"
FILE = "database.db"

STATIONS = {
    'Paris': ("FRPLY",),
    'Montpellier': ("FRMPL",)
}

CITIES = {
    'Paris': 'FRPAR',
    'Montpellier': 'FRMPT'
}

SCHEDULES = {
    'M': ( datetime.time(hour=0),  datetime.time(hour=14) ),
    'A': ( datetime.time(hour=14), datetime.time(hour=19) ),
    'E': ( datetime.time(hour=19), datetime.time(hour=23, minute=59) ),
    'D': ( datetime.time(hour=0),  datetime.time(hour=23, minute=59) )
}