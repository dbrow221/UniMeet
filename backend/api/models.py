from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Student Union Ballroom"
    address = models.TextField(blank=True, null=True)  # optional full address
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name



class Event(models.Model):
    name = models.CharField(max_length=50)
    details = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="events")
    is_public = models.BooleanField(default=True)  # 👈 new field

    def __str__(self):
        return f"{self.name} @ {self.location.name}"
    

