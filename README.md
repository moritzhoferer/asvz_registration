# Automatic ASVZ registration (free classes only)

This tool allows you to automatically register for your favorite ASVZ lesson when the registration period opens. This is especially helpful for highly demanded lessons, like indoor cycling classes.

Note that the script does not save any data or passwords.

## Why?

[ASVZ](https://asvz.ch/) is the academic sports association of the universities in Zurich.
The registration procedure should be rethought, because its already a competition to register for a popular class because the registration works by first-come-first-serve. Popular classes are booked out in seconds. As an example: If someone has to work in a restaurant at a given time to finance their studies, they do not have time to look at their smartphone at a specific time to register. Many students programmed bots and made it harder to register. These people have an clear advantage.

My suggestion is opened earlier (36 hours before the class) and the registrations of the first 12 hours are distributed randomly? If there are still places available after that, it is first come, first serve. Wouldn't that be fairer?

I communicated this to the ASVZ, but they were not interested in a fairer solution. Therefore, I think everybody should have a bot to register. :)

## Instruction

First build your own file which stores your preferences.
The file has format like the snippet below.
The snippet shows all possible filters. If one filter is not needed it either can be deleted or set to `null`.
Weekdays are number form 0 (Monday) to 6 (Sunday).

```json
{
    "title": "30min HIT-Training",
    "sport": "Cycling Class",
    "weekday": 1,
    "time": "hh:mm",
    "instructor": ["Name Surname"],
    "location": "Sport Center Polyterrasse"
}
```

The start the program with the json file storing your preference `venv/bin/python3 asvz_registration.py preferences.json`.

For Cycling classes at Polyterrasse, you also can start the program for a weekday (First 3 letters) and time (wiht or without ":") with `venv/bin/python3 asvz_registration.py mon 19:30`.

## Setup

First, you install the [Firefox browser](https://www.mozilla.org/en-US/firefox/new/). Then, the [geckodriver for Firefox](https://github.com/mozilla/geckodriver/releases) and either add it to PATH or adjust `webdriver.Firefox(executable_path='geckodriver')` with the right path. I recommend to setup a Python environment in the directory of the repository:

```{bash}
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## TODOs

* [ ] Add options (sport -s `-s`, weekday `-w`, date `-d`,time `-t`, location `-l`) for the executable file.
* [ ] Interactive Input to select a class.
* [ ] Clean the code and put everything into functions.
* [ ] *Maybe:* Adapt to other logins.
