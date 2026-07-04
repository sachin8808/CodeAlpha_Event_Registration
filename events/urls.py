from django.urls import path

from . import views

urlpatterns = [
    # ---- HTML pages ----
    path("", views.home, name="home"),
    path("event/<int:pk>/", views.event_detail, name="event_detail"),
    path("event/<int:pk>/register/", views.register_for_event_page, name="register_for_event_page"),
    path("my-registrations/", views.my_registrations_page, name="my_registrations"),
    path("registration/<int:pk>/cancel/", views.cancel_registration_page, name="cancel_registration_page"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ---- JSON API ----
    path("api/events/", views.api_events_list, name="api_events_list"),
    path("api/events/<int:pk>/", views.api_event_detail, name="api_event_detail"),
    path("api/events/<int:pk>/register/", views.api_event_register, name="api_event_register"),
    path("api/registrations/", views.api_my_registrations, name="api_my_registrations"),
    path("api/registrations/<int:pk>/cancel/", views.api_registration_cancel, name="api_registration_cancel"),
]
