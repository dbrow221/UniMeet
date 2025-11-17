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

    def is_expired(self):
        """Check if the event has already ended."""
        return timezone.now() > self.end_time

    def clean(self):
        """Ensure end_time is after start_time."""
        from django.core.exceptions import ValidationError
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def save(self, *args, **kwargs):
        """Validate before saving to the database."""
        self.full_clean()  # runs clean() before saving
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    pronouns = models.CharField(max_length=50, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    profile_picture = models.URLField(blank=True, max_length=500)

    def __str__(self):
        return self.user.username


class JoinRequest(models.Model):
    """Tracks requests to join private events."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="join_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'user')  # Prevent duplicate requests
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.event.name} ({self.status})"


class Comment(models.Model):
    """Comments on events."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']  # Oldest first

    def __str__(self):
        return f"{self.user.username} on {self.event.name}: {self.text[:50]}"
  

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"
    

class Friendship(models.Model):
    """Represents a friendship between two users."""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"    
    
class UserSearch(models.Model):
    """Model to track user search queries."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="searches")
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} searched for '{self.query}' at {self.timestamp}"    