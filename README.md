# AutomaticTimeTracker
A program that tracks your time across all applications and websites from the moment you open your computer to the moment you close it. It updates Google Calendar with the time spent and adds it to a database to be able to query later.

<img width="623" alt="Screenshot 2023-10-26 054657" src="https://github.com/ZiadElGafy/AutomaticTimeTracker/assets/74333133/79f339fa-13f8-4ca1-a8e9-53456c749fa2">

## Step 1: Get access to your Google Calendar

1. Head to https://console.cloud.google.com
2. From the sidebar under "IAM & Admin" select "Create a Project".
3. After creating the project, from the sidebar under "APIs and Services" click "Enabled APIs & Services".
4. Search for "Google Calendar API" and enable it.
5. From the sidebar, select "OAuth consent screen"
6. Pick "External" and press create.
7. Add the app name and your email as the support email. (If you encounter problems in this step add yourself as a collaborator and tester in your project on https://console.firebase.google.com)
8. In the scopes tab, click "ADD OR REMOVE SCOPES" and make sure to check all scopes labeled with "Google Calendar API".
9. Under "OAuth user cap", add your email as a test user.
10. From the sidebar, click "Credentials".
11. Click "CREATE CREDENTIALS", and then "OAuth client ID".
12. Set the type to "Desktop app", and click create.
13. Download the JSON file, rename it to `credentials.json`, and put it in the *GoogleCalendarManager* folder.

*Don't share your credentials or token with anyone as they are private.*

## Step 2: Customize the scripts to make them your own

You will find the following in the `timeTracker.pyw` file in the *TimeTracker* folder.

<img width="780" alt="Screenshot 2023-10-26 014826" src="https://github.com/ZiadElGafy/AutomaticTimeTracker/assets/74333133/536cb184-e475-4760-adcf-faa55ff984ea">

And the following in the `googleCalendarManager.pyw` file in the *GoogleCalendarManager* folder.

<img width="748" alt="Screenshot 2023-10-26 014606" src="https://github.com/ZiadElGafy/AutomaticTimeTracker/assets/74333133/789ad873-eeda-44c3-9ddf-a838e208ba55">

*You can get your calendar's ID from the calendar's settings under the Integrate Calendar section.*

*If you don't know your timezone, you can get it from here* https://www.timezoneconverter.com/cgi-bin/zonehelp.tzc

In the same file, you will find these two dictionaries that need to be filled.

<img width="600" alt="Screenshot 2023-10-26 060632" src="https://github.com/ZiadElGafy/AutomaticTimeTracker/assets/74333133/36db3151-b482-4228-bc21-797eedb7f838">

Make sure to update these variables and save the files.

## Step 3: Create the time tracking database

Run the `createTable.py` file in the *GoogleCalendarManager* folder once to create the table where your time entries will be stored.

You can modify the columns in the table and their values as you like.

<img width="527" alt="Screenshot 2023-10-26 054810" src="https://github.com/ZiadElGafy/AutomaticTimeTracker/assets/74333133/2f3a55e5-d377-4735-bf3a-a80bbd05790b">

The scripts now work just fine and will track the time spent on your active applications and websites and update Google Calendar and the database accordingly.

## To make the scripts run on startup:

Create a `.bat` file in the same directory as the `timeTracker.pyw` file and write the following in it:

```
@echo off
python (PATH TO YOUR timeTracker.pyw FILE)
```

Now, press `Windows + R` and write `shell:startup`

In the directory that got opened create a `.vbs` file and write the following in it:

```
CreateObject("Wscript.Shell").Run "PATH TO YOUR .bat FILE",0,True
```

The `timeTracker.pyw` and `googleCalendarManager.pyw` files were created in the `.pyw` format rather than `.py` to prevent them from opening a terminal when running.

### You're all set! Enjoy not having to manually track your time or update Google Calendar again.
