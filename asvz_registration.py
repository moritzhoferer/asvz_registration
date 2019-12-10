#!/usr/bin/python3.6

import pandas as pd
from time import sleep
import datetime
import dateutil.parser

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_credentials() -> list:
    from getpass import getpass 
    print('Enter data of the user to register!')
    usr = input('Enter user: ')
    pwd = getpass('Enter password: ')
    return [usr, pwd]


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
        _df = _df[_df.title == _filter['title']]

    if 'sport' in _filter.keys():
        _df = _df[_df.sport_name == _filter['sport']]

    if 'weekday' in _filter.keys():
        _df = _df[_df.to_date.apply(lambda x: x.weekday == _filter['weekday'])]

    if 'time' in _filter.keys():
        _df = _df[_df.to_date.apply(lambda x: x.time() == _filter['time'])]

    if 'instructor' in _filter.keys():
        _df = _df[_df.instructor_name.notna()]
        _df[_df.instructor_name.apply(lambda x: _filter['instructor'] == x)]  

    if 'location' in _filter.keys():
        _df = _df[_df.location == _filter['location']]
    return _df


if __name__ == '__main__':
    # Enter username and password of the user to register
    # TODO Check for correctness of the credentials
    usr, pwd = get_credentials()
    # Preferred lesson: Dictionary with filters
    preferred_lesson = {
        # 'title': '30min HIT-Training',  # Title
        'sport': 'Cycling Class',  # Sport
        'weekday': 1,  # Monday: 0, Tuesday: 1, ..., Sunday: 6
        'time': datetime.time(18, 00),  # datetime.time(h, m)
        'instructor': ['Zbinden, Sofia'], # ['Surname, Name']
        'location': 'Sport Center Polyterrasse' # Location
    }

    # Load the lesson schedule "Sportfahrplan" and filter of the desired lesson
    sportfahrplan = get_sportfahrplan(filter=preferred_lesson)
    
    # find the next lesson you want to register for
    next_lesson = sportfahrplan.iloc[0]

    registration_time = next_lesson.oe_from_date.astimezone(tz=datetime.timezone.utc)
    time_now = datetime.datetime.now().astimezone(tz=datetime.timezone.utc)
    waiting_period = (registration_time - time_now).total_seconds()

    # Wait until 5 seconds before the registration opens
    # sleep(waiting_period - 5)
    # time_start = datetime.datetime.now()
    # TODO Open browser in headless mode
    # driver_options = Options()
    # driver_options.headless = True
    driver = webdriver.Firefox()
    
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

    # time_end = datetime.datetime.now()
    # delta_time = time_end - time_start
    # print('The login took approx. {sec:.2f} seconds.'.format(sec=delta_time.total_seconds()))
    
    # Finally, register for the lesson
    lesson_login_button = driver.find_element_by_id('btnRegister')
    lesson_login_button.click()
    # Quit browser
    driver.quit()
