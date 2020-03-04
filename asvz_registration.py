#!/usr/bin/python3

import sys
import pandas as pd
import json
from time import sleep
import datetime
import dateutil.parser
import pytz
import requests as re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

cet_tz = pytz.timezone('CET')


def open_firefox(headless=True):
    _driver_options = Options()
    if headless:
        _driver_options.add_argument('-headless')
    return webdriver.Firefox(executable_path='geckodriver', options=_driver_options)


# TODO Rename to enter_credentials
def get_credentials() -> list:
    from getpass import getpass
    print('Enter data of the user to register!')
    _usr = input('Enter username: ')
    _pwd = getpass('Enter password: ')
    return [_usr, _pwd]


# TODO implement correctness check
# TODO Maybe add this to get_credentials as option check_correctness=True
# def check_asvz_login(_driver, _usr, _pwd):
#     # ASVZ login
#     asvz_login_url = 'https://auth.asvz.ch/account/login'
#     _driver.get(asvz_login_url)
#     switchAai_button = _driver.find_element_by_xpath('//*[@title="SwitchAai Account Login"]') 
#     switchAai_button.click()
#     # This can be skipped if the university is saved in the browser's chache
#     if _driver.current_url.startswith('https://wayf.switch.ch/'):
#         # Select institution to get to ETH Login
#         input_box = _driver.find_element_by_id('userIdPSelection_iddtext')
#         input_box.send_keys('ETH Zurich')
#         send_button = _driver.find_element_by_name('Select')
#         send_button.click()
#     user_box = _driver.find_element_by_id('username')
#     user_box.send_keys(_usr)
#     password_box = _driver.find_element_by_id('password')
#     password_box.send_keys(_pwd)
#     login_button = _driver.find_element_by_id('LoginButtonText')
#     login_button.click()  


def get_sportfahrplan(entries=2000, filter=None) -> pd.DataFrame:
    # Specific search for Cycling classes
    _request = re.get('https://asvz.ch/asvz_api/event_search?_format=json&limit={e:d}'.format(e=entries))
    _results = _request.json()['results']
    # TODO Reduce columns to the necessary ones
    _df = pd.DataFrame(_results)
    # Just export lessons which need a registration and are not cancelled
    _df = _df[(_df.cancelled == False) &
              _df.oe_enabled &
              (_df.oe_from_date.notnull()) &
              (_df.from_date.notnull())]
    # Format relevant times to CET
    _df.oe_from_date = _df.oe_from_date.apply(lambda x: dateutil.parser.parse(x).astimezone(tz=cet_tz))
    _df.from_date = _df.from_date.apply(lambda x: dateutil.parser.parse(x).astimezone(tz=cet_tz))
    if filter:
        _df = filter_sportfahrplan(_df, filter)
    return _df.sort_values(by='oe_from_date', ascending=True)


def get_next_lesson(filter: dict = None):
    # Load the lesson schedule "Sportfahrplan" and filter of the desired lesson
    if filter is None:
        filter = {}
    _sportfahrplan = get_sportfahrplan(filter=filter)
    # Find the next lesson with free places you want to register for
    _sportfahrplan = _sportfahrplan[_sportfahrplan.places_free > 0]
    return _sportfahrplan.iloc[0]


def filter_sportfahrplan(_df, _filter) -> pd.DataFrame:
    if 'title' in _filter.keys():
        if _filter['title']:
            _df = _df[_df.title == _filter['title']]

    if 'sport' in _filter.keys():
        if _filter['sport']:
            _df = _df[_df.sport_name == _filter['sport']]

    if 'weekday' in _filter.keys():
        if _filter['weekday'] is not None:
            _df = _df[_df.from_date.apply(lambda x: x.weekday == _filter['weekday'])]

    if 'time' in _filter.keys():
        if _filter['time']:
            _df = _df[_df.from_date.apply(lambda x: x.time() == _filter['time'])]

    if 'instructor' in _filter.keys():
        if _filter['instructor']:
            _df = _df[_df.instructor_name.notna()]
            _df = _df[_df.instructor_name.apply(lambda x: x == _filter['instructor'])]

    if 'location' in _filter.keys():
        if _filter['location']:
            _df = _df[_df.location == _filter['location']]
    return _df


def get_lesson_info(s: pd.Series):
    string = '{sport:s} with {instr:s} on {d:d}.{m:d}.{y:d} at {hour:2d}:{minute:02d}h at {loc:s}.'
    sport = s.sport_name
    instructor = ' '
    for name in [i.split(' ')[0] for i in s.instructor_name]:
        instructor += name + '& '
    instructor = instructor[1:-2]
    location = s.location
    day = s.from_date.day
    month = s.from_date.month
    year = s.from_date.year
    hour = s.from_date.hour
    minute = s.from_date.minute
    print(string.format(sport=sport, instr=instructor, d=day, m=month, y=year,
                        hour=hour, minute=minute, loc=location))


def get_time_until(t) -> int:
    _time_now = datetime.datetime.now(tz=cet_tz)
    _waiting_period = (t - _time_now).total_seconds()
    return _waiting_period


def load_preferences(file_name: str) -> dict:
    with open(file_name, 'r') as file:
        _dict = json.load(file)
    if 'time' in _dict.keys():
        if _dict['time']:
            hour, minute = _dict['time'].split(':')
            _dict['time'] = datetime.time(int(hour), int(minute), tzinfo=cet_tz)
    return _dict


def make_preferences(argv: list) -> dict:
    _dict = {"title": None, "sport": "Cycling Class", "weekday": None, "time": None, "instructor": [],
             "location": "Sport Center Polyterrasse"}
    weekday: str = argv[1].lower()
    if weekday == 'mon':
        _dict['weekday'] = 0
    elif weekday == 'tue':
        _dict['weekday'] = 1
    elif weekday == 'wed':
        _dict['weekday'] = 2
    elif weekday == 'thu':
        _dict['weekday'] = 3
    elif weekday == 'fri':
        _dict['weekday'] = 4
    elif weekday == 'sat':
        _dict['weekday'] = 5
    elif weekday == 'sun':
        _dict['weekday'] = 6
    else:
        raise IOError

    _day_time = argv[2]
    if ':' in _day_time:
        hour, minute = argv[2].split(':')
    else:
        hour, minute = _day_time[:-2], _day_time[2:]
    _dict['time'] = datetime.time(int(hour), int(minute), tzinfo=cet_tz)

    return _dict


# TODO def main():
# def main():
#     get_credentials()
#     get_next_lesson()
#     wait() Maybe change be integrated in the next function
#     register_for_lession()


if __name__ == '__main__':
    # TODO Change all dates to Timezone Europe/Rome for convenience
    # TODO Facilitate code structure
    driver = open_firefox()
    driver.get('https://auth.asvz.ch/account/login')
    switchAai_button = driver.find_element_by_xpath('//*[@title="SwitchAai Account Login"]')
    switchAai_button.click()

    # Skip if the selection of the institution is saved in the browser's chache
    if driver.current_url.startswith('https://wayf.switch.ch/'):
        # Select institution to get to ETH Login
        input_box = driver.find_element_by_id('userIdPSelection_iddtext')
        input_box.send_keys('ETH Zurich')
        send_button = driver.find_element_by_name('Select')
        send_button.click()

    while True:
        # Enter username and password of the user to register
        usr, pwd = get_credentials()
        # Enter credentials
        user_box = driver.find_element_by_id('username')
        user_box.clear()
        user_box.send_keys(usr)
        password_box = driver.find_element_by_id('password')
        password_box.send_keys(pwd)
        login_button = driver.find_element_by_id('LoginButtonText')
        login_button.click()

        try:
            driver.find_element_by_xpath('//*[@class="validation_false validation_info"]')
            print('Authentication failed! Username, password or both are wrong.')
        except NoSuchElementException:
            print('Authentication successfully checked!')
            driver.quit()
            break
    # Preferred lesson: Dictionary with filters
    if len(sys.argv) == 2:
        lesson_filter = load_preferences(sys.argv[1])
    elif len(sys.argv) == 3:
        lesson_filter = make_preferences(sys.argv)
    else:
        lesson_filter = {}
    try:
        next_lesson = get_next_lesson(lesson_filter)
    except IndexError:
        next_lesson = get_next_lesson()
    get_lesson_info(next_lesson)
    registration_time = next_lesson.oe_from_date.astimezone(tz=cet_tz)

    # Wait until 1 minute before the registration opens to start with login
    waiting_period = get_time_until(registration_time) - 60
    if waiting_period > 0:
        print(
            'Wait for {h:.0f}h {m:.0f}m {s:.0f}s until login'
                .format(h=waiting_period / 60 // 60, m=waiting_period / 60 % 60, s=waiting_period % 60)
        )
        sleep(waiting_period)

    # TODO def register_for_lession(lession: pd.Series, usr, pwd)
    # Open browser in headless mode
    # driver_options = Options()
    # driver_options.add_argument('-headless')
    # driver = webdriver.Firefox(executable_path='geckodriver', options=driver_options)
    driver = open_firefox()

    driver.get(next_lesson.url)
    login_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@class="btn btn-default ng-star-inserted"]')))
    if login_button.text == "LOGIN":
        login_button.click()
        # Select identification via Switch Aai
        switchAai_button = driver.find_element_by_xpath('//*[@title="SwitchAai Account Login"]')
        switchAai_button.click()
        # Skip if the selection of saved in the browser's chache
        if driver.current_url.startswith('https://wayf.switch.ch/'):
            # Select institution to get to ETH Login
            input_box = driver.find_element_by_id('userIdPSelection_iddtext')
            input_box.send_keys('ETH Zurich')
            send_button = driver.find_element_by_name('Select')
            send_button.click()
        # Enter credentials
        user_box = driver.find_element_by_id('username')
        user_box.send_keys(usr)
        password_box = driver.find_element_by_id('password')
        password_box.send_keys(pwd)
        login_button = driver.find_element_by_id('LoginButtonText')
        login_button.click()

    print('Ready for registration.')
    # Wait until the registration is opened and finally, register for the lesson
    lesson_login_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@class="btn-primary btn enrollmentPlacePadding ng-star-inserted"]')))
    lesson_login_button.click()
    # Quit browser
    driver.quit()
