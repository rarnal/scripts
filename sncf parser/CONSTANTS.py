import datetime
import CONFIG

ROOT_URL = "https://www.oui.sncf/calendar/"
PERIOD_LOOKUP_INTERVAL = 90


msg_yy = ("""Hello my beautiful,\n\nThis is just an email to tell you that you are beautiful and I'm in love with you.\n\n""" +
                   """You are wonderful. I love you.\n\nOnce again, I love you.\n\nHave a good morning my beautiful girl :)\n\n""" +
                   """Oh additionnally, check in attachment and you'll see the cheaper train for a given destination destination.\n\n""" +
                   """I'll check how to send that kind of email every day.\n\nLove you, love you, love you again and forever\n\n""")

JOURNEYS = (
    {
        'departure': 'Paris',
        'arrival': 'London',    # Beware that the departure and arrival cities are referenced in CONSTANTS.CITIES
        'schedules': ((5, 7),), # the digits represent a week day (1 being monday and 7 sunday)tuple because we can insert several schedules
                                # Tuple in order to let the possibiliy to have several schedules for a trip - example: ((5, 7), 6, 7))
        'time_depart': "17h00",
        'time_arrival': "16h00",
        'max_price': 150,
        'email': CONFIG.recipients_1, # in the format "myaddress@gmail.com;my_other_address@gmail.com"
        'body': msg_yy, # the email body message, just a string
        'low_cost': False,
    },                          
    {
        'departure': 'Paris',
        'arrival': 'Montpellier',
        'schedules': ((5, 7),),
        'time_depart': "17h00",
        'time_arrival': "16h00",
        'max_price': 150,
        'email': CONFIG.recipients_1,
        'body': msg_yy,
        'low_cost': False,
    },
    {
        'departure': 'Paris',
        'arrival': 'Avignon',
        'schedules': ((5, 7),),
        'time_depart': "17h00",
        'time_arrival': "16h00",
        'max_price': 150,
        'email': CONFIG.recipients_1,
        'body': msg_yy,
        'low_cost': False,
    },
    # {
    #     'departure': 'Avignon',
    #     'arrival': 'Barcelona',
    #     'schedules': None,
    #     'time_depart': "00h00",
    #     'time_arrival': "00h00",
    #     'max_price': 150,
    #     'email': CONFIG.recipients_2,
    #     'body': "Regarde la pièce jointe ! Les prix affichés sont pour l'aller et retour",
    #     'low_cost': False,
    # },
    # {
    #     'departure': 'Avignon',
    #     'arrival': 'Paris',
    #     'schedules': None,
    #     'time_depart': "00h00",
    #     'time_arrival': "17h00",
    #     'max_price': 150,
    #     'email': CONFIG.recipients_2,
    #     'body': "Regarde la pièce jointe ! Les prix affichés sont pour l'aller et retour",
    #     'low_cost': True,
    # },
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
    'London': "GBLON",
    'Barcelona': "ESBCN"
}

SCHEDULES = {
    'M': ( datetime.time(hour=0),  datetime.time(hour=14) ),
    'A': ( datetime.time(hour=14), datetime.time(hour=19) ),
    'E': ( datetime.time(hour=19), datetime.time(hour=23, minute=59) ),
    'D': ( datetime.time(hour=0),  datetime.time(hour=23, minute=59) )
}
