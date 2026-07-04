"""
Views for the Event Registration app.

There are two "layers" here on purpose:

1. HTML pages (home, event_detail, my_registrations_page, etc.)
   -> so you can test everything just by clicking around in a browser.

2. JSON API endpoints (all under /api/...)
   -> so the app satisfies "build API endpoints" and can be tested
      with curl / Postman / any frontend framework later.

Both layers share the same underlying models and logic.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Event, Registration


def json_login_required(view_func):
    """
    Like Django's @login_required, but returns a proper JSON 401
    instead of redirecting to the login page (which doesn't make
    sense for an API that returns JSON).
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required. Please log in first."}, status=401
            )
        return view_func(request, *args, **kwargs)

    return wrapper


# --------------------------------------------------------------------------
# HTML PAGES
# --------------------------------------------------------------------------

def home(request):
    events = Event.objects.all()
    return render(request, "events/home.html", {"events": events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    already_registered = False
    if request.user.is_authenticated:
        already_registered = Registration.objects.filter(
            user=request.user, event=event, cancelled=False
        ).exists()
    return render(
        request,
        "events/event_detail.html",
        {"event": event, "already_registered": already_registered},
    )


@login_required
def register_for_event_page(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        existing = Registration.objects.filter(user=request.user, event=event).first()
        if existing and not existing.cancelled:
            messages.info(request, "You're already registered for this event.")
        elif event.is_full and not (existing and existing.cancelled):
            messages.error(request, "Sorry, this event is full.")
        elif existing and existing.cancelled:
            existing.cancelled = False
            existing.cancelled_at = None
            existing.save()
            messages.success(request, "You're registered again!")
        else:
            Registration.objects.create(user=request.user, event=event)
            messages.success(request, "You're registered for this event!")
    return redirect("event_detail", pk=pk)


@login_required
def my_registrations_page(request):
    registrations = Registration.objects.filter(user=request.user).select_related("event")
    return render(request, "events/my_registrations.html", {"registrations": registrations})


@login_required
def cancel_registration_page(request, pk):
    reg = get_object_or_404(Registration, pk=pk, user=request.user)
    if request.method == "POST" and not reg.cancelled:
        reg.cancelled = True
        reg.cancelled_at = timezone.now()
        reg.save()
        messages.success(request, "Registration cancelled.")
    return redirect("my_registrations")


def register_view(request):
    """Simple sign-up page so you can create a test account without /admin."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        email = request.POST.get("email", "").strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "That username is already taken.")
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            login(request, user)
            messages.success(request, "Account created! You're logged in.")
            return redirect("home")

    return render(request, "events/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password.")

    return render(request, "events/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


# --------------------------------------------------------------------------
# JSON API
# --------------------------------------------------------------------------

def _event_to_dict(event, detailed=False):
    data = {
        "id": event.id,
        "title": event.title,
        "location": event.location,
        "date_time": event.date_time.isoformat(),
        "capacity": event.capacity,
        "spots_left": event.spots_left,
        "is_full": event.is_full,
    }
    if detailed:
        data["description"] = event.description
        data["organizer"] = event.organizer.username if event.organizer else None
    return data


def api_events_list(request):
    """GET /api/events/ - list every event."""
    events = Event.objects.all()
    return JsonResponse({"events": [_event_to_dict(e) for e in events]})


def api_event_detail(request, pk):
    """GET /api/events/<id>/ - details for one event."""
    event = get_object_or_404(Event, pk=pk)
    return JsonResponse(_event_to_dict(event, detailed=True))


@csrf_exempt
@json_login_required
@require_http_methods(["POST"])
def api_event_register(request, pk):
    """POST /api/events/<id>/register/ - register the logged-in user for an event."""
    event = get_object_or_404(Event, pk=pk)
    existing = Registration.objects.filter(user=request.user, event=event).first()

    if existing and not existing.cancelled:
        return JsonResponse({"error": "Already registered for this event."}, status=409)

    if event.is_full and not (existing and existing.cancelled):
        return JsonResponse({"error": "This event is full."}, status=409)

    if existing and existing.cancelled:
        existing.cancelled = False
        existing.cancelled_at = None
        existing.save()
        registration = existing
    else:
        registration = Registration.objects.create(user=request.user, event=event)

    return JsonResponse(
        {
            "id": registration.id,
            "event_id": event.id,
            "event": event.title,
            "user": request.user.username,
            "registered_at": registration.registered_at.isoformat(),
        },
        status=201,
    )


@json_login_required
def api_my_registrations(request):
    """GET /api/registrations/ - list the logged-in user's registrations."""
    registrations = Registration.objects.filter(user=request.user).select_related("event")
    data = [
        {
            "id": r.id,
            "event_id": r.event.id,
            "event_title": r.event.title,
            "registered_at": r.registered_at.isoformat(),
            "cancelled": r.cancelled,
        }
        for r in registrations
    ]
    return JsonResponse({"registrations": data})


@csrf_exempt
@json_login_required
@require_http_methods(["POST", "DELETE"])
def api_registration_cancel(request, pk):
    """POST or DELETE /api/registrations/<id>/cancel/ - cancel a registration."""
    reg = get_object_or_404(Registration, pk=pk, user=request.user)
    if reg.cancelled:
        return JsonResponse({"error": "Already cancelled."}, status=400)
    reg.cancelled = True
    reg.cancelled_at = timezone.now()
    reg.save()
    return JsonResponse({"id": reg.id, "cancelled": True})
