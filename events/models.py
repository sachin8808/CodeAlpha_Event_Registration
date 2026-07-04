from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    """A single event that people can register for."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    date_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(
        default=0, help_text="Maximum number of attendees. Use 0 for unlimited."
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
        help_text="The event organizer (optional).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_time"]

    def __str__(self):
        return self.title

    @property
    def active_registrations_count(self):
        """How many people are currently registered (not cancelled)."""
        return self.registrations.filter(cancelled=False).count()

    @property
    def spots_left(self):
        """Returns None if capacity is unlimited (0), otherwise remaining spots."""
        if self.capacity == 0:
            return None
        return max(self.capacity - self.active_registrations_count, 0)

    @property
    def is_full(self):
        if self.capacity == 0:
            return False
        return self.active_registrations_count >= self.capacity


class Registration(models.Model):
    """Links a user to an event they've signed up for."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registrations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # A user can only have ONE registration row per event
        # (we reuse/uncancel it instead of creating duplicates).
        unique_together = ("user", "event")
        ordering = ["-registered_at"]

    def __str__(self):
        status = "cancelled" if self.cancelled else "active"
        return f"{self.user.username} -> {self.event.title} ({status})"
