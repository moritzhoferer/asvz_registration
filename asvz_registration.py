#!/usr/bin/python3.6

import requests as re
# import pprint
# import webbrowser
# import pyautogui
# import time
import dateutil.parser

login_url = 'https://auth.asvz.ch/account/login'

# Find button to ETH Login via SwitchAai
# Enter email to id='username' and password to id='password'

# Continue finding the right lession

# Preferred weekday
# Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
preferredWeekday = 2  # type: int

# preferred time as ['hh','mm','ss']
preferredTime= ['18', '30', '00']

# preferred Instructor
preferredInstructor: str = 'Baumgartner, Rico' # 'Surname, Name'

preferred_location = None

# Dictionary containing the features of the preferred lession
preferred_lesson = {
    'weekday': None,
    'time': None,
    'instructor': None
}

# Load the lesson schedule "Sportfahrplan" and filter of the desired lesson
a = re.get('https://asvz.ch/asvz_api/event_search?_format=json&limit=60&f[0]=sport:45645&availability=1&f[1]=facility:'
           '45594&selected=f0:checkbox_availability:f1')
text = a.json()

# print(type(text))
# print(text)
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(text)
# pp.pprint(text["results"][0]["url"])

for i, iDetails in enumerate(text['results']):
    if iDetails['instructor_name'] == [preferredInstructor]:
        dateTime = dateutil.parser.parse(iDetails['from_date'])
        print(dateTime)

# url = text["results"][0]["url"]
#
# course_re = re.get(url)
# print(course_re.text)
# course = course_re.json()

# pp.pprint(course)
# webbrowser.open_new_tab(url)
#
# time.sleep(3)
#
# pyautogui.click(500, 300)
