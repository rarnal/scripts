# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import re
import datetime
import collections

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import oauth2client
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import mimetypes
import os

from apiclient import errors

import CONSTANTS
import CONFIG   # I use this file to store some variable (always commented). 
                # I don't share this file as it contains sensitive information, especially regarding the gmail API
                # You'll have to get your own system to send emails if you want to reuse this script
                # More information here: https://developers.google.com/gmail/api/quickstart/python

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class playground:
    def __init__(self):
        self.conn = sqlite3.connect(CONFIG.DATABASE)
    

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


def get_time(t):
    hour, minute = map(int, t.split('h'))
    return datetime.time(hour=hour, minute=minute)


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

        here = open("here.html", "w")
        reshtml = res.to_html(here)
        here.close()

        
        message = ""
        for x in range(len(res)):
            message += f"""
                {res.at[x, "Total_price"]} € - {res.at[x, "Departure"]} to {res.at[x, "Arrival"]} from {res.at[x, "Depart_date"]} {res.at[x, "Depart_time"]} to {res.at[x, "Return_date"]} {res.at[x, "Return_time"]}
            """

        message = ("""Hello my beautiful,\n\nThis is just an email to tell you that you are beautiful and I'm in love with you.\n\n""" +
                   """You are wonderful. I love you.\n\nOnce again, I love you.\n\nHave a good morning my beautiful girl :)\n\n""" +
                   """Oh additionnally, check in attachment and you'll see the cheaper train for a given destination destination.\n\n""" +
                   """I'll check how to send that kind of email every day.\n\nLove you, love you, love you again and forever\n\n""")

        
        
        create_and_send_email(
            to = CONFIG.gmail_recipients,
            subject = f"{datetime.date.today().isoformat()} - Trains from {journey['departure']} to {journey['arrival']}",
            message = message,
            filename= "here.html",
            file_dir=CONFIG.file_dir
        )



def create_and_send_email(to, subject, message, file_dir, filename):
    credentials = get_credentials()
    service = build('gmail', 'v1', http=credentials.authorize(Http()))
    user_id = 'me'
    sender = CONFIG.gmail_sender
    request_url = f"https://www.googleapis.com/gmail/v1/users/{CONFIG.gmail_sender}/messages/send"

    #formatted_message = create_message(sender, to, subject, message)
    formatted_message = create_message_with_attachment(sender, to, subject, message, file_dir, filename)
    send_email(service, user_id, formatted_message)
    


def send_email(service, user_id, message):
    # https://developers.google.com/gmail/api/v1/reference/users/messages/send#examples
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def create_message(sender, to, subject, message_text):
    # https://developers.google.com/gmail/api/v1/reference/users/messages/send#examples
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


# thank you....
# http://programmingsolutions24x7.blogspot.com/2017/01/sending-mail-using-google-auth-in-python.html
def get_credentials():    
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CONFIG.SECRET_FILE, CONFIG.SCOPES)
        flow.user_agent = CONFIG.APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_message_with_attachment(sender, to, subject, message_text, file_dir, filename):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_dir: The directory containing the file to be attached.
        filename: The name of the file to be attached.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    if main_type == 'text':
        fp = open(path, 'r')
        msg = MIMEText(fp.read().encode().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(path, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(path, 'ru')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}



# to use once only in order to link our python project with our gmail account

def script_to_authentificate_gmail_session():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time
    

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', CONFIG.SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])


if __name__=="__main__":
    draft_email()