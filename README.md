# Automatic ASVZ registration
This tool allows you to automatically register for your favorite ASVZ lesson when the registration period opens. This is especially helpful for highly demanded lessons, like Cycling Classes.

## Purpose
The registration procedure should be rethought.
*Describe problem*, *Suggest solution*.

## Instruction
First build your own file which stores your preferences.
The file has format like the snippet below.
The snippet shows all possible filters. If one filter is not needed it either can be deleted or set to `null`.

```json
{
    "title": '30min HIT-Training',  # Title
    "sport": 'Cycling Class',  # Sport
    "weekday": 1,  # Monday: 0, Tuesday: 1, ..., Sunday: 6
    "time": "hh:mm",  # Hour:minute
    "instructor": ['Surname, Name'], # ['Surname, Name']
    "location": 'Sport Center Polyterrasse' # Location
}
```
The start the program with the json file storing your preference `python3 asvz_registration.py preferences.json`.

For Cycling classes at Polyterrasse, you also can start the program for a weekday (First 3 letters) and time (wiht or without ":") with `python3 asvz_registration.py mon 19:30`.

## TODOs

* Clean the code and put everything into functions.
* *Maybe:* Adapt to other logins.
