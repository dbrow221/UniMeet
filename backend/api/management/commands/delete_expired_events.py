from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Event  

class Command(BaseCommand):
    help = "Deletes events whose end_time has already passed."

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_events = Event.objects.filter(end_time__lt=now)
        count = expired_events.count()
        expired_events.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} expired events."))
