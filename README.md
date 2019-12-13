# Automatic ASVZ registration
This tool allows you to automatically register for your favorite ASVZ lesson when the registration period opens. This is especially helpful for highly demanded lessons, like Cycling Classes.

## Purpose
The registration procedure should be rethought.
*Describe problem*, *Suggest solution*.

## Instruction
First build you own file which stores your preferences.
The file has format like the snippet below. The snippet shows all possible filters. If one filter is not need it either can be deleted or set to `null`.
```
{
    'title': '30min HIT-Training',  # Title
    'sport': 'Cycling Class',  # Sport
    'weekday': 1,  # Monday: 0, Tuesday: 1, ..., Sunday: 6
    'time': "hh:mm",  # Hour:minute
    'instructor': ['Surname, Name'], # ['Surname, Name']
    'location': 'Sport Center Polyterrasse' # Location
}
```
*Either set up cron job or start job in background*


## TODOs
* Add infinite modular waiting loop of <= 1h.
* Adjust as an always running job or as cron job with store password
* Store preferred lesson in json or csv file
* Multiple preferred lessons.
