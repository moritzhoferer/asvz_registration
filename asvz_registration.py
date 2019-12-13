#!/usr/bin/python3.6

import sys
import pandas as pd
import json
from time import sleep
import datetime
import dateutil.parser

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


def open_Firefox(headless=True):
    driver_options = Options()
    if headless: driver_options.add_argument('-headless')
    return webdriver.Firefox(executable_path='geckodriver', options=driver_options)


def get_credentials() -> list:
    from getpass import getpass 
    print('Enter data of the user to register!')
    usr = input('Enter user: ')
    pwd = getpass('Enter password: ')
    return [usr, pwd]


# TODO Function to check credentials
# def check_credentials(usr, pwd) -> bool:


def check_asvz_login(_driver, _usr, _pwd):
    # ASVZ login
    asvz_login_url = 'https://auth.asvz.ch/account/login'
    _driver.get(asvz_login_url)
    switchAai_button = _driver.find_element_by_xpath('//*[@title="SwitchAai Account Login"]') 
    switchAai_button.click()
    # This can be skipped if the university is saved in the browser's chache
    if _driver.current_url.startswith('https://wayf.switch.ch/'):
        # Select institution to get to ETH Login
        input_box = _driver.find_element_by_id('userIdPSelection_iddtext')
        input_box.send_keys('ETH Zurich')
        send_button = _driver.find_element_by_name('Select')
        send_button.click()
    user_box = _driver.find_element_by_id('username')
    user_box.send_keys(_usr)
    password_box = _driver.find_element_by_id('password')
    password_box.send_keys(_pwd)
    login_button = _driver.find_element_by_id('LoginButtonText')
    login_button.click()
    # TODO implement correctness check


def get_sportfahrplan(entries = 2000, filter=None) -> pd.DataFrame:
    import requests as re
    # Specific search for Cycling classes
    request = re.get('https://asvz.ch/asvz_api/event_search?_format=json&limit={e:d}'.format(e=entries))
    results = request.json()['results']
    _df = pd.DataFrame(results)
    # Just export lessons which need a registration and are not cancelled
    _df = _df[_df.cancelled == False]
    _df = _df[_df.oe_from_date.notna()]
    _df.oe_from_date = _df.oe_from_date.apply(lambda x: dateutil.parser.parse(x))
    _df.to_date = _df.to_date.apply(lambda x: dateutil.parser.parse(x))
    if filter:
        _df = filter_sportfahrplan(_df, filter)   
    return _df.sort_values(by='oe_from_date', ascending=True)


def filter_sportfahrplan(_df, _filter) -> pd.DataFrame:
    if 'title' in _filter.keys():
        if _filter['title']:
            _df = _df[_df.title == _filter['title']]

    if 'sport' in _filter.keys():
        if _filter['sport']:
            _df = _df[_df.sport_name == _filter['sport']]

    if 'weekday' in _filter.keys():
        if _filter['weekday']:
            _df = _df[_df.to_date.apply(lambda x: x.weekday == _filter['weekday'])]

    if 'time' in _filter.keys():
        if _filter['time']:
            _df = _df[_df.to_date.apply(lambda x: x.time() == _filter['time'])]

    if 'instructor' in _filter.keys():
        if _filter['instructor']:
            _df = _df[_df.instructor_name.notna()]
            _df = _df[_df.instructor_name.apply(lambda x: x == _filter['instructor'])]  

    if 'location' in _filter.keys():
        if _filter['location']:
            _df = _df[_df.location == _filter['location']]
    return _df


def get_lesson_info(s: pd.Series):
    # TODO Bring this output in a nice format!
    print(s.sport_name)
    print(s.to_date)
    print(s.instructor_name)
    print(s.location)


def get_time_until(t) -> int:
    time_now = datetime.datetime.now().astimezone(tz=datetime.timezone.utc)
    waiting_period = (t - time_now).total_seconds()
    return waiting_period


def load_preferences(file_name: str):
    with open(file_name, 'r') as file:
        dict_ = json.load(file)
    if 'time' in dict_.keys():
        if dict_['time']:
            hour, minute = dict_['time'].split(':')
            dict_['time'] = datetime.time(int(hour), int(minute))
    return dict_


if __name__ == '__main__':    
    driver = open_Firefox()
    driver.get('https://auth.asvz.ch/account/login')
    switchAai_button = driver.find_element_by_xpath('//*[@title="SwitchAai Account Login"]') 
    switchAai_button.click()

    # Skip if the selection of saved in the browser's chache
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
    if len(sys.argv) > 1:
        preferred_lesson = load_preferences(sys.argv[1])
    else:
        preferred_lesson = {}

    # Load the lesson schedule "Sportfahrplan" and filter of the desired lesson
    sportfahrplan = get_sportfahrplan(filter=preferred_lesson)
    # find the next lesson with free places you want to register for
    sportfahrplan = sportfahrplan[sportfahrplan.places_free > 0]
    next_lesson = sportfahrplan.iloc[0]
    get_lesson_info(next_lesson)
    registration_time = next_lesson.oe_from_date.astimezone(tz=datetime.timezone.utc)

    # Wait until 1 minute before the registration opens to login
    waiting_period = get_time_until(registration_time) - 60
    if waiting_period > 0:
        print(
            'Waiting for {h:.0f}h {m:.0f}m {s:.0f}s until login'
            .format(h=waiting_period/60//60, m=waiting_period/60%60, s=waiting_period%60)
        )
        sleep(waiting_period)
    
    # Open browser in headless mode
    driver_options = Options()
    driver_options.add_argument('-headless')
    driver = webdriver.Firefox(executable_path='geckodriver', options=driver_options)
    
    driver.get(next_lesson.url)
    login_button = login_button = driver.find_element_by_xpath('//*[@class="btn btn-default ng-star-inserted"]')
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
            # remember_checkbox = driver.find_element_by_id('rememberForSession')
            # remember_checkbox.click()
            send_button = driver.find_element_by_name('Select')
            send_button.click()
        # Enter credentials
        user_box = driver.find_element_by_id('username')
        user_box.send_keys(usr)
        password_box = driver.find_element_by_id('password')
        password_box.send_keys(pwd)
        login_button = driver.find_element_by_id('LoginButtonText')
        login_button.click()

    # Wait until the registration is opened
    waiting_period = get_time_until(registration_time) + 2
    if waiting_period > 0:
        print('Wait for {sec:.1f} minutes until registration'.format(sec=waiting_period))
        sleep(waiting_period)
    # Finally, register for the lesson
    lesson_login_button = driver.find_element_by_id('btnRegister')
    lesson_login_button.click()
    # Quit browser
    driver.quit()
