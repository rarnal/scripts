import datetime

ROOT_URL = "https://www.oui.sncf/calendar/"
DATABASE = "/home/romain/var/www/html/scripts/sncf parser/database2.db"

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