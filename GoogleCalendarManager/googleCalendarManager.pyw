from __future__ import print_function

import datetime
import os.path
import pytz
from sys import argv

import sqlite3

from datetime import datetime
from datetime import timedelta
from dateutil import parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


PATH_OF_THIS_PROJECT = "" # Path from where this will be run to the project folder
CALENDARID = "" # "Primary" if its the main calendar
TIMEZONE = "" # Find your timezone here "https://www.timezoneconverter.com/cgi-bin/zonehelp.tzc"
TIMEZONEOFFSET = # The offset of your timezone (e.g. GMT + 5 would be 5)

SCOPES = ['https://www.googleapis.com/auth/calendar']
DATETIMEFORMAT = "%Y-%m-%d %H:%M:%S"
TIMEEPS = 300

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(PATH_OF_THIS_PROJECT + '/GoogleCalendarManager/token.json'):
        creds = Credentials.from_authorized_user_file(PATH_OF_THIS_PROJECT + '/GoogleCalendarManager/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH_OF_THIS_PROJECT + '/GoogleCalendarManager/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(PATH_OF_THIS_PROJECT + '/GoogleCalendarManager/token.json', 'w') as token:
            token.write(creds.to_json())

    # Get event details from argv
    if len(argv) > 1 and argv[1] == "add":
        title = argv[2]
        description = argv[3]
        
        date = datetime.strptime(argv[4], '%Y-%m-%d').date()
        time = datetime.strptime(argv[5], '%H:%M:%S').time()
        secondsToRemove = timedelta(seconds = time.second)
        start = datetime.combine(date, time) - secondsToRemove
        duration = float(argv[6])
        color = int(argv[7])

        addEventToCalendar(creds, title, description, start, duration, color)
        addEventToDB(creds, title, description, start, duration)

def combineDescriptions(first, second):
    if len(first) > 1:
        first = first[:-1]
    
    if len(second) > 1:
        second = second[:-1]
    
    firstSegments = first.split(', ')
    secondSegments = second.split(', ')
    
    distinct = set()
    distinct.update(firstSegments)
    distinct.update(secondSegments)
    if '.' in distinct:
        distinct.remove('.')

    ret = ""

    for word in distinct:
        if ret:
            ret += ', '
        
        ret += word
    
    ret += '.'
    return ret

def addEventToCalendar(creds, title, description, start, duration, color):
    try:
        end = start + timedelta(hours = duration)

        service = build('calendar', 'v3', credentials = creds)

        today = datetime.now().date()
        yesterday = today - timedelta(hours = 24)
        startTime = str(yesterday) + "T00:00:00Z"
        endTime = str(today) + "T23:59:59Z"
        
        # getting recent events
        events_result = service.events().list(calendarId = CALENDARID,
                                                timeMin = startTime,
                                                timeMax = endTime,
                                                singleEvents = True,
                                                orderBy = 'startTime',
                                                timeZone = TIMEZONE).execute()
        
        events = events_result.get('items', [])

        eventsToEdit = []

        for event in events:
            eventStart = event['start'].get('dateTime', event['start'].get('date'))
            eventEnd = event['end'].get('dateTime', event['end'].get('date'))

            startFormatted = parser.isoparse(eventStart)
            startFormatted = startFormatted.replace(tzinfo = None)
            endFormatted = parser.isoparse(eventEnd)
            endFormatted = endFormatted.replace(tzinfo = None)

            if (endFormatted - start).seconds <= TIMEEPS and event['summary'] == title:
                eventsToEdit.append([event, description])

        for event in eventsToEdit:
            eventId = event[0]['id']

            # get start and end in google calendar api's format
            eventStart = event[0]['start'].get('dateTime', event[0]['start'].get('date'))
            eventEnd = event[0]['end'].get('dateTime', event[0]['end'].get('date'))

            # get start and end in datetime format
            startFormatted = parser.isoparse(eventStart)
            endFormatted = parser.isoparse(eventEnd)

            # remove the timezone
            startFormatted = startFormatted.replace(tzinfo = None)
            endFormatted = endFormatted.replace(tzinfo = None)

            # fix the timezone offset
            startFormatted -= timedelta(hours = TIMEZONEOFFSET)
            endFormatted -= timedelta(hours = TIMEZONEOFFSET)

            # extend the previous event with the duration of this one
            endFormatted += timedelta(hours = duration)

            # change the start and end to google calendar api's format
            startFormatted = startFormatted.isoformat() + 'Z'
            endFormatted = endFormatted.isoformat() + 'Z'

            body = {
                'summary': title,
                'colorId': color,
                'description': combineDescriptions(event[0]['description'] if 'description' in event[0] else '', description),
                'start': {
                    'dateTime': startFormatted,
                    'timeZone': TIMEZONE,
                },
                'end': {
                    'dateTime': endFormatted,
                    'timeZone': TIMEZONE,
                },
            }

            service.events().update(calendarId = CALENDARID,
                                    eventId = eventId,
                                    body = body).execute()
            
            print("Event updated successfully")
            return
        
        start -= timedelta(hours = TIMEZONEOFFSET) # apply timezone changes
        end = start + timedelta(hours = duration)
        
        startFormatted = start.isoformat() + 'Z'
        endFormatted = end.isoformat() + 'Z'

        event = {
            'summary': title,
            'colorId': color,
            'description': description,
            'start': {
                'dateTime': startFormatted,
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': endFormatted,
                'timeZone': TIMEZONE,
            },
        }    

        service = build('calendar', 'v3', credentials = creds)
        event = service.events().insert(calendarId = CALENDARID, body = event).execute()
        print('Event created successfully')
        print('%s' % (event.get('htmlLink')))
    except HttpError as error:
        print('An error occurred: %s' % error)

def addEventToDB(creds, title, description, start, duration):
    conn = sqlite3.connect(PATH_OF_THIS_PROJECT + '/GoogleCalendarManager/timeTrackingHours.db')
    ptr = conn.cursor()
    print("Established connection with database successfully")

    rows = ptr.execute('SELECT * FROM hours WHERE CATEGORY = ?', (title,)).fetchall()

    if len(rows):
        lastRow = rows[-1]
        prevTitle = lastRow[1]
        prevStart = datetime.strptime(lastRow[0], DATETIMEFORMAT)
        prevDuration = float(lastRow[3])

        if (prevTitle.lower() == title.lower() and prevStart + timedelta(hours = prevDuration) - start).seconds <= TIMEEPS:
            duration += prevDuration
            start = prevStart
            minTime = prevStart - timedelta(seconds = TIMEEPS)
            maxTime = prevStart + timedelta(seconds = TIMEEPS)
            ptr.execute('DELETE FROM hours WHERE DATETIME BETWEEN ? AND ?', (minTime, maxTime))

    tableEntry = (start, title, description, duration)
    ptr.execute("INSERT INTO hours VALUES(?, ?, ?, ?);", tableEntry)
    conn.commit()
    print("Hours logged into database successfully")

if __name__ == '__main__':
    main()
