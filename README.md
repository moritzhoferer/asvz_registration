# Automatic ASVZ registration

This tool allows you to automatically register for your favorite ASVZ lesson when the registration period opens. This is especially helpful for highly demanded lessons, like Cycling Classes.

## Purpose

The registration procedure should be rethought.
*Describe problem*, *Suggest solution*.

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

First install the [Firefox browser](https://www.mozilla.org/en-US/firefox/new/) and [geckodriver for Firefox](https://github.com/mozilla/geckodriver/releases). I recommend to setup a python environment named "venv" in the directory of the repository with

```{bash}
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## TODOs

* [ ] Clean the code and put everything into functions.
* [ ] *Maybe:* Adapt to other logins.
* [ ] Interactive Input to select a class.
