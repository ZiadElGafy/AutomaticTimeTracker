import os
import time
import datetime
import win32gui
import uiautomation as auto

from win32gui import GetForegroundWindow, GetWindowText
from win32process import GetWindowThreadProcessId
from pywinauto.application import Application
from subprocess import call

PATH_OF_THIS_PROJECT = "" # Path from where this will be run to the project folder
SLEEPDELAY = 10 # How often the program gets the active window (in seconds)
COMMITDELAY = 15 * 60 # How often the program commits time to the calendar and database (in seconds)

activeWindow = ""
lastCommit = datetime.datetime.now()
startTime = datetime.datetime.now()
timeSpent = {}

def getNameFromURL(url):
    linkPartitions = url.split('/')
    return linkPartitions[2]

def getChromeURL():
    window = GetForegroundWindow()
    tID, pID = GetWindowThreadProcessId(window)
    app = Application(backend = "uia").connect(process = pID, time_out = 10)
    dlg = app.top_window()
    title = "Address and search bar"
    url = ""
    try:
        url = dlg.child_window(title = title, control_type = "Edit").get_value()
    except:
        url = ""
    return "https://" + url

categories = {
    # Fill this up according to your uses with any part of the name of the app or website, ex:
    # 'Productivity': ['gmail', 'slack', 'sheets.google', 'docs.google']
    # 'Entertainment': ['youtube', 'Spotify']
    # 'Coding': ['Visual Studio Code', 'stackoverflow', 'github']
}

color = {
    # Fill this up to style your calendar
    # 'Productivity': 7,
    # 'Entertainment': 9,
    # 'Coding': 3,

    # 0: Calendar color
    # 1: Lavender
    # 2: Sage
    # 3: Grape
    # 4: Flamingo
    # 5: Banana
    # 6: Tangerine
    # 7: Peacock
    # 8: Graphite
    # 9: Blueberry
    # 10: Basil
    # 11: Tomato
}

def getColor(category):
    if category in color:
        return color[category]
    
    return 10

def categorize(app):
    if app == '':
        return "Idle"
    
    for category in categories:
        for subString in categories[category]:
            if subString in app:
                return category
            
    return app

# Add time spent to calendar and database
def commitTime():
    categories = {}
    for app in timeSpent:
        category = categorize(app)

        if category not in categories:
            categories.update({category: 0})
        categories[category] += timeSpent[app]

    mostUsedCategory = max(categories, key = categories.get)
    description = ""

    added = set()
    for app in timeSpent:
        namePartitions = app.split('-')
        name = namePartitions[-1].strip()

        if name not in added:
            if description:
                description = description + ", "
            
            description = description + name
            added.add(name)

    description += '.'

    now = datetime.datetime.now()
    now -= datetime.timedelta(seconds = COMMITDELAY)
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    call(["python", PATH_OF_THIS_PROJECT + "/GoogleCalendarManager/googleCalendarManager.pyw", "add", mostUsedCategory, description, date, time, str(COMMITDELAY / 60 / 60), str(getColor(mostUsedCategory))])

    timeSpent.clear()

while True:
    newActiveWindow = GetWindowText(GetForegroundWindow())

    if "Google Chrome" in newActiveWindow:
        newActiveWindow = getNameFromURL(getChromeURL())

    now = datetime.datetime.now()

    if newActiveWindow != activeWindow:
        if activeWindow not in timeSpent:
            timeSpent.update({activeWindow: 0})

        timeSpent[activeWindow] += (now - startTime).seconds

        activeWindow = newActiveWindow
        startTime = now
        print(activeWindow)

    if (now - lastCommit).seconds >= COMMITDELAY:
        if activeWindow not in timeSpent:
            timeSpent.update({activeWindow: 0})

        timeSpent[activeWindow] += (now - startTime).seconds
        
        commitTime()
        print("Time committed successfully at: ", now.time())

        startTime = now
        lastCommit = now

    time.sleep(SLEEPDELAY)
