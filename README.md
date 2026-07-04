# Event Registration System

A backend system for browsing events and registering to attend them, built with Django. Made as part of my CodeAlpha internship.

## What it does

- Lists upcoming events with date, location, and how many spots are left
- Lets logged-in users register for an event
- Lets users view all their registrations and cancel one if their plans change
- Stops people from registering twice for the same event, and stops registrations once an event is full
- Comes with a free admin panel where an event organizer can add/edit events and see who's registered, without touching any code

## Tech used

- **Backend:** Python (Django)
- **Database:** SQLite (Django's default, zero setup needed)
- **Frontend:** Django templates with plain HTML/CSS — no JS framework

## Running it locally

1. Clone the repo
```
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Set up the database (creates the tables)
```
python manage.py makemigrations
python manage.py migrate
```

4. Create an admin/organizer account
```
python manage.py createsuperuser
```

5. Run the server
```
python manage.py runserver
```

6. Open your browser to `http://127.0.0.1:8000/` for the site, or `http://127.0.0.1:8000/admin/` to log in as the organizer and add events.

## API endpoints

| Method | Route | What it does |
|--------|-------|---------------|
| GET | `/api/events/` | List all events |
| GET | `/api/events/<id>/` | Get details for one event |
| POST | `/api/events/<id>/register/` | Register the logged-in user for an event |
| GET | `/api/registrations/` | List the logged-in user's registrations |
| POST | `/api/registrations/<id>/cancel/` | Cancel a registration |

The API endpoints use session-based login, so you need to log in through the site (`/login/`) in the same browser/session before calling them, or pass session cookies along if testing with curl/Postman.

## Things I'd like to add later

- Token-based authentication so the API can be used without a browser session
- Email confirmation when someone registers
- Waitlists for full events
- Search/filter on the events list
- Deploying it somewhere instead of just localhost

## Notes

Built to practice Django's models, views, templates, auth system, and admin panel together in one small project.
