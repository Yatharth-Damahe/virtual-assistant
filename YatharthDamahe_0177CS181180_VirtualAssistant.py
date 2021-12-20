
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pyttsx3
import time

import speech_recognition as sr
import pytz
import subprocess
import re
import webbrowser
from email.mime.text import MIMEText
from email import errors
import base64
from datetime import date
import imdb
import wikipedia




# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/calendar.readonly","https://www.googleapis.com/auth/gmail.send"]
# for calender
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]


def speak(text):
    engine=pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate = engine.getProperty('rate')

    engine.setProperty('rate', rate-20)

    engine.say(text)
    engine.runAndWait()




def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio=r.listen(source)
        said=""

    try:
        said=r.recognize_google(audio)
        print(said)

    except:
        print("Didn't get that")

    return said.lower()











def authenticate_calender():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service
def get_events(day,service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc=pytz.UTC
    date=date.astimezone(utc)
    end=end.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),timeMax=end.isoformat(),
                                         singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time=str(start.split("T")[1].split("+")[0])   #it will split by T and then take the 1st index i.e right of T and same process for "+"
            p=start_time.split(":")[0]
            if int(p)<12:
                start_time=p+"a m"

            else:
                start_time=str(int(p)-12)+start_time.split(":")[1]
                start_time=start_time+"p m"
            speak(event["summary"]+"at"+start_time)

'''service=authenticate_calender()
get_events(2,service)'''
def get_date(text):
    text=text.lower()
    today=datetime.date.today()

    if text.count("today")>0:
        return today

    day=-1
    day_of_week=-1
    month=-1
    year=today.year

    for word in text.split():
        if word in MONTHS:
            month=MONTHS.index(word)+1
        elif word in DAYS:
            day_of_week=DAYS.index(word)
        elif word.isdigit():
            day=int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found=word.find(ext)
                if found>0:
                    try:
                        day=int(word[:found])  #5th t is index=1so it slice for word[:1] and then it give 5
                    except:
                        pass


    if month<today.month and month!=-1:  # if the month mentioned is before the current month set the year to the next
        year=year+1

    if month==-1 and day!=-1:
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    if month==-1 and day==-1 and day_of_week!=-1:
        current_day_of_week=today.weekday()
        diff=day_of_week-current_day_of_week


        if diff<0:
            diff+=7
            if text.count("next"):
                diff+=7

        return today+datetime.timedelta(diff)
    if day==-1 or month==-1:
        return None

    return datetime.date(month=month,day=day,year=year)




def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service













def check_mails(service):



    today = (date.today())

    today_main = today.strftime('%Y/%m/%d')

    # Call the Gmail API
    results = service.users().messages().list(userId='me',labelIds=["INBOX","UNREAD"],q="after:{0} and category:Primary".format(today_main)).execute()


    messages=results.get('messages',[])


    if not messages:
        print('No messages found.')
        speak('No messages found.')
    else:
        m=""
        speak("{} new emails found".format(len(messages)))

        speak("if you want to read any particular email just say read ")
        speak("and for not reading say leave or wait for sometime it will pass")
        for message in messages:

            msg=service.users().messages().get(userId='me',id=message['id'],format='metadata').execute()

            for add in msg['payload']['headers']:
                if add['name']=="From":

                    a=str(add['value'].split("<")[0])
                    #print(a)


                    speak("email from"+a)
                    #text=get_audio()


                    if get_audio() == "read":


                        speak(msg['snippet'])

                    else:
                        speak("email passed")

def send_email(service):

    email_from="me"
    speak("Enter email id of receipient")

    email_to=input()
    speak("Subject of the email")
    email_subject=get_audio()
    speak("What content do you want to send?")
    email_content=get_audio()

    message=MIMEText(email_content)
    message['to']=email_to
    message['from']=email_from
    message['subject']=email_subject
    raw=base64.urlsafe_b64encode(message.as_bytes())    #way of reading content to send
    raw=raw.decode()
    body={'raw':raw}


    try:
        message=(service.users().messages().send(userId='me',body=body).execute())
        speak("Your message is sent")
    except errors.MessageError as error:
        speak("error occured")


def search_movie():


    moviesdb=imdb.IMDb()




    #serach for title
    speak("which movie you wanna search about?")
    text=get_audio()
    movies=moviesdb.search_movie(text)

    speak("Seraching for "+ text)
    if len(movies)==0:
        speak("No result found")
    else:
        speak("If you want to know more about any one of them just say information after name")
        speak("I found these:")

        for movie in movies:

            title=movie['title']
            year=movie['year']



            #speak("If you want to know more about any of them just say information after name")
            speak(f'{title}-{year}')


            text=get_audio()
            if text=='information':

                info=movie.getID()
                movie=moviesdb.get_movie(info)

                title=movie['title']
                year=movie['year']
                rating=movie['rating']
                plot=movie['plot outline']


                if year<int(datetime.datetime.now().strftime("%Y")):
                    speak(f'{title}was released in {year} has IMDB rating of {rating}.The plot summary of movie is{plot}')
                    break

                else:
                    speak(f'{title}will release in {year} has IMDB rating of {rating}.The plot summary of movie is{plot}')
                    break








def note(text):
    speak("What should be the name of file")
    file_name = get_audio()

    with open(file_name,"w") as f:
        f.write(text)


    subprocess.Popen(['notepad.exe',file_name])

def web_browser(text):

    print("running")

    if text.split(sep=" "):
        domain = text.split(sep=" ")[1]
        print(domain)
        url='https://www.'+domain

        webbrowser.register('chrome',None,webbrowser.BackgroundBrowser(r"C:\Users\windows\AppData\Local\Google\Chrome\Application\chrome.exe"))
        webbrowser.get('chrome').open(url)
        speak("You reached the website destination")
    else:
        speak("didn't get that")

def get_current_time():

    time=datetime.datetime.now().strftime("%I %M %p")
    speak("The current time is "+time)

def current_date():

    date=str(datetime.datetime.today())
    date=date.split(" ")[0]
    date=date.split("-")
    year=date[0]
    month=MONTHS[int(date[1])-1]
    day=date[2]

    speak("Date is "+day+month+year)


def greet():

    hour=datetime.datetime.now().strftime("%I %p")
    if "PM" in hour:
        if int(hour.split(" ")[0])>5 and int(hour.split(" ")[0])<12 :
            speak("Hello Yatharth, Good evening. How may I help you?")
        else:
            speak("Hello Yatharth, Good Afternoon. How may I help you?")
    else:
        speak("Hello Yatharth, Good morning. How may I help you?")


def wiki_info():
    speak("What do you want to know about")
    text=get_audio()
    speak("Searching for "+text)
    speak(wikipedia.summary(text,5))









SERVICE=authenticate_calender()
SERVICE2=authenticate_gmail()
print("start")

def main():
    WAKE = "hello world"
    text = get_audio()
    if text.count(WAKE) > 0:
        greet()
        while(True):
            print("Listening")


            text=get_audio()

            Calender_strings=["what do i have","what plans do i have"," am i busy on","what plan do i have","do i have plans on","do i have any plans on"]

            for phrase in Calender_strings:
                if phrase in text:
                    date = get_date(text)
                    if date:
                            get_events(date,SERVICE)
                    else:
                        speak("I don't understand")

            Note_strings=["make a note","write this down","remember this"]
            for phrase in Note_strings:
                if phrase in text:
                    speak("What would you like me to write down? ")
                    note_text=get_audio()
                    note(note_text)
                    speak("I have made that note for you.")

            Web_strings=['open','start']
            for phrase in Web_strings:
                if phrase in text:
                    print("successful")

                    web_browser(text)

            Time_strings=["current time","ongoing time","is time","what time is it"]
            for phrase in Time_strings:
                if phrase in text:
                    get_current_time()

            Date_strings=["today's date","today date"]
            for phrase in Date_strings:
                if phrase in text:
                    current_date()

            Check_mails=["check emails",'check mails','check mail','check email']
            for phrase in Check_mails:
                if phrase in text:
                    check_mails(SERVICE2)



            Send_email=["send mail","send email"]
            for phrase in Send_email:
                if phrase in text:
                    send_email(SERVICE2)

            Movies_search=['check about movies','pictures','search for a movie','search for movies']
            for phrase in Movies_search:
                if phrase in text:
                    search_movie()

            wikipedia_info=["search for me","tell me ","give me information"]
            for phrase in wikipedia_info:
                if phrase in text:

                    wiki_info()



            Signing_of=["thanks","thank you"]
            for phrase in Signing_of:
                if text in Signing_of:


                        speak("This is star signing off")
                        exit()

main()




