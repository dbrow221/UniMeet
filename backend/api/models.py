from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# Helper functions for default times
def default_start_time():
    return timezone.now()

def default_end_time():
    return timezone.now() + timedelta(hours=1)


# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Student Union Ballroom"
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("name", "latitude", "longitude")

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=50)
    details = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="events")
    is_public = models.BooleanField(default=True)
    start_time = models.DateTimeField(default=default_start_time)
    end_time = models.DateTimeField(default=default_end_time)
    max_capacity = models.PositiveIntegerField(default=10)
    participant_list = models.ManyToManyField(User, related_name="joined_events", blank=True)

    def __str__(self):
        return f"{self.name} @ {self.location.name}"

    def is_full(self):
        """Check if the event has reached its max capacity."""
        return self.participant_list.count() >= self.max_capacity

    def clean(self):
        """Ensure end_time is after start_time."""
        from django.core.exceptions import ValidationError
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def save(self, *args, **kwargs):
        """Validate before saving to the database."""
        self.full_clean()  # runs clean() before saving
        super().save(*args, **kwargs)
