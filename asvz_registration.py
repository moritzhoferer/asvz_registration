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
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

cet_tz = pytz.timezone('CET')


def open_firefox(headless=True):
    print('Opening Firefox...')
    from selenium.webdriver.firefox.options import Options
    _driver_options = Options()
    if headless:
        _driver_options.add_argument('-headless')
    return webdriver.Firefox(executable_path='geckodriver', options=_driver_options)


def open_chrome(headless=True):
    print('Opening Chrome...')
    from selenium.webdriver.chrome.options import Options
    _driver_options = Options()
    if headless:
        _driver_options.add_argument('-headless')
    return webdriver.Chrome(executable_path='chromedriver', options=_driver_options)


def enter_credentials() -> list:
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
#     # This can be skipped if the university is saved in the browser's cache
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


def get_sportfahrplan(entries=2000, filter_=None) -> pd.DataFrame:
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
    if filter_:
        _df = filter_sportfahrplan(_df, filter_)
    return _df.sort_values(by='oe_from_date', ascending=True)


def get_next_lesson(filter_: dict = None):
    # Load the lesson schedule "Sportfahrplan" and filter of the desired lesson
    if filter_ is None:
        filter_ = {}
    _sportfahrplan = get_sportfahrplan(filter_=filter_)
    # Find the next lesson with free places you want to register for
    _sportfahrplan = _sportfahrplan[_sportfahrplan.places_free > 0]
    return _sportfahrplan.iloc[0]


def filter_sportfahrplan(df, filter_) -> pd.DataFrame:
    if 'title' in filter_.keys():
        if filter_['title']:
            df = df[df.title == filter_['title']]

    if 'sport' in filter_.keys():
        if filter_['sport']:
            df = df[df.sport_name == filter_['sport']]

    if 'weekday' in filter_.keys():
        if filter_['weekday'] is not None:
            df = df[df.from_date.apply(lambda x: x.weekday == filter_['weekday'])]

    if 'time' in filter_.keys():
        if filter_['time']:
            df = df[df.from_date.apply(lambda x: x.time() == filter_['time'])]

    if 'instructor' in filter_.keys():
        if filter_['instructor']:
            df = df[df.instructor_name.notna()]
            df = df[df.instructor_name.apply(lambda x: x == filter_['instructor'])]

    if 'location' in filter_.keys():
        if filter_['location']:
            df = df[df.location == filter_['location']]
    return df


def print_lesson_info(s: pd.Series) -> None:
    string = '{sport:s} with {instr:s} on {d:d}.{m:d}.{y:d} at {hour:2d}:{minute:02d}h at {loc:s}.'
    sport = s.sport_name
    instructor = ' '
    for name in [i.split(' ')[0] for i in s.instructor_name]:
        instructor += name + ' & '
    instructor = instructor[1:-3]
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
    _dict = {"title": None, "sport": None, "weekday": None, "time": None, "instructor": [],
             "location": None}
    
    _dict["sport"] = argv[1]
    if _dict["sport"] == "Cycling Class":
        _dict["location"] = "Sport Center Polyterrasse"

    if _dict["sport"] == "Rennvelo":
        _dict["title"] = "Treff"
    
    weekday: str = argv[2].lower()
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

    _day_time = argv[3]
    if ':' in _day_time:
        _hour, _minute = _day_time
    else:
        _hour, _minute = _day_time[:-2], _day_time[2:]
    _dict['time'] = datetime.time(int(_hour), int(_minute), tzinfo=cet_tz)

    return _dict


# TODO def main():
# def main():
#     get_credentials()
#     get_next_lesson()
#     wait() Maybe change be integrated in the next function
#     register_for_lesson()


if __name__ == '__main__':
    # TODO Facilitate code structure
    driver = open_chrome(headless=False)
    driver.get('https://auth.asvz.ch/account/login')
    switchAai_button = driver.find_element_by_xpath('//*[@title="SwitchAai Account Login"]')
    switchAai_button.click()

    # Skip if the selection of the institution is saved in the browser's cache
    if driver.current_url.startswith('https://wayf.switch.ch/'):
        # Select institution to get to ETH Login
        input_box = driver.find_element_by_id('userIdPSelection_iddtext')
        input_box.send_keys('ETH Zurich')
        send_button = driver.find_element_by_name('Select')
        send_button.click()

    while True:
        # Enter username and password of the user to register
        usr, pwd = enter_credentials()
        # Enter credentials
        user_box = driver.find_element_by_id('username')
        user_box.clear()
        user_box.send_keys(usr)
        password_box = driver.find_element_by_id('password')
        password_box.send_keys(pwd)
        # login_button = driver.find_element_by_id('LoginButtonText')
        login_button = driver.find_element_by_name('_eventId_proceed')
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
    elif len(sys.argv) == 4:
        lesson_filter = make_preferences(sys.argv)
    else:
        lesson_filter = {}
    try:
        next_lesson = get_next_lesson(lesson_filter)
    except IndexError:
        next_lesson = get_next_lesson()
    print_lesson_info(next_lesson)
    registration_time = next_lesson.oe_from_date.astimezone(tz=cet_tz)

    # Wait until 1 minute before the registration opens to start with login
    waiting_period = get_time_until(registration_time) - 60
    if waiting_period > 0:
        print(
            'Wait for {h:.0f}h {m:.0f}m {s:.0f}s until login'
            .format(h=waiting_period / 60 // 60, m=waiting_period / 60 % 60, s=waiting_period % 60)
        )
        sleep(waiting_period)

    # TODO def register_for_lesson(lesson: pd.Series, usr, pwd)
    driver = open_chrome()
    wait_slow = WebDriverWait(driver, 90, poll_frequency=.1)
    driver.get(next_lesson.url)
    login_button = wait_slow.until(
        ec.element_to_be_clickable((By.XPATH, '//*[@class="btn btn-default ng-star-inserted"]')))
    if login_button.text == "LOGIN":
        login_button.click()
        # Select identification via Switch Aai
        switchAai_button = wait_slow.until(
            ec.element_to_be_clickable((By.XPATH,'//*[@title="SwitchAai Account Login"]'))
        )
        switchAai_button.click()
        # Skip if the selection of saved in the browser's cache
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
        # login_button = driver.find_element_by_id('LoginButtonText')
        login_button = driver.find_element_by_name('_eventId_proceed')
        login_button.click()

    print('Ready for registration.')
    # Wait until the registration is opened and finally, register for the lesson
    wait_quick = WebDriverWait(driver, 90, poll_frequency=.005)
    lesson_login_button = wait_quick.until(
        ec.element_to_be_clickable((By.XPATH, '//*[@class="btn-primary btn enrollmentPlacePadding ng-star-inserted"]'))
    )
    lesson_login_button.click()
    print('Registration successfully completed.')
    # Quit browser
    driver.quit()
