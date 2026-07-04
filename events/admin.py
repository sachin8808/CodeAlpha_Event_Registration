from django.contrib import admin

from .models import Event, Registration


class RegistrationInline(admin.TabularInline):
    """Shows registrations right on the Event's admin page."""

    model = Registration
    extra = 0
    readonly_fields = ("user", "registered_at", "cancelled", "cancelled_at")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date_time",
        "location",
        "capacity",
        "organizer",
        "active_registrations_count",
    )
    list_filter = ("date_time",)
    search_fields = ("title", "location")
    inlines = [RegistrationInline]

    @admin.display(description="Registered")
    def active_registrations_count(self, obj):
        return obj.active_registrations_count


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "registered_at", "cancelled")
    list_filter = ("cancelled", "event")
    search_fields = ("user__username", "event__title")
