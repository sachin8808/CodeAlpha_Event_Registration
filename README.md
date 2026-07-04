# Event Registration System

Second CodeAlpha task - this one's an event registration system. People can look through a list of events, sign up for the ones they want to attend, and cancel later if they change their mind. Built with Django since it comes with an admin panel out of the box, which made sense for letting an "organizer" manage events without needing a separate dashboard built from scratch.

## Stack

- Django (Python)
- SQLite
- Django templates for the pages, no frontend framework

## What it does

- Browse a list of upcoming events with date, location and spots remaining
- Sign up / log in as a regular user
- Register for an event
- View your own registrations and cancel one if needed
- Stops you from registering twice for the same thing, and stops registrations once an event fills up
- Organizers get the Django admin panel for free - add events, see who registered, all without touching code

## Setup

```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then go to `http://127.0.0.1:8000/admin/` first, log in with the superuser you just made, and add an event so there's something to actually look at on the main site (`http://127.0.0.1:8000/`).

## API endpoints

| Method | URL | Does what |
|---|---|---|
| GET | /api/events/ | list of events |
| GET | /api/events/<id>/ | one event's details |
| POST | /api/events/<id>/register/ | register for it |
| GET | /api/registrations/ | your registrations |
| POST | /api/registrations/<id>/cancel/ | cancel one |

These use normal Django session login, so you need to be logged in through the site itself before hitting them (or pass cookies if testing with Postman/curl).

## Notes

Used the same user (Registration) row for cancel + re-register instead of creating a new row every time someone toggles their registration, otherwise the unique constraint on user+event would throw an error. That took a bit of trial and error to get right.

## Possible improvements later

- Token auth so the API doesn't need a browser session
- Waitlist for full events
- Email when you register or cancel
- Search/filter on the events page
