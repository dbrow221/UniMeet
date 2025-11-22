from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from api.models import Event, Notification, Friendship


class Command(BaseCommand):
    help = 'Generate friend event reminders for upcoming events'

    def handle(self, *args, **kwargs):
        """
        Find events starting in the next 2 hours and create notifications 
        for friends of participants (not already notified).
        """
        now = timezone.now()
        reminder_window_start = now
        reminder_window_end = now + timedelta(hours=2)

        # Find events starting within the next 2 hours
        upcoming_events = Event.objects.filter(
            start_time__gte=reminder_window_start,
            start_time__lte=reminder_window_end
        ).prefetch_related('participant_list')

        notifications_created = 0

        for event in upcoming_events:
            # Get all participants of this event
            participants = event.participant_list.all()

            for participant in participants:
                # Find friends of this participant
                # Friends can be in either user1 or user2 position
                friendships_as_user1 = Friendship.objects.filter(user1=participant).values_list('user2_id', flat=True)
                friendships_as_user2 = Friendship.objects.filter(user2=participant).values_list('user1_id', flat=True)
                
                friend_ids = set(friendships_as_user1) | set(friendships_as_user2)

                # Create notifications for friends who:
                # 1. Are not already participating in the event
                # 2. Haven't already been notified about this event
                for friend_id in friend_ids:
                    # Skip if friend is already participating
                    if event.participant_list.filter(id=friend_id).exists():
                        continue

                    # Check if notification already exists
                    existing_notification = Notification.objects.filter(
                        user_id=friend_id,
                        event=event,
                        notification_type='friend_event_reminder'
                    ).exists()

                    if not existing_notification:
                        # Create the notification
                        time_until_event = event.start_time - now
                        hours = int(time_until_event.total_seconds() // 3600)
                        minutes = int((time_until_event.total_seconds() % 3600) // 60)
                        
                        if hours > 0:
                            time_str = f"{hours} hour{'s' if hours > 1 else ''}"
                        else:
                            time_str = f"{minutes} minute{'s' if minutes > 1 else ''}"

                        message = f"Your friend {participant.username} is attending '{event.name}' in {time_str}!"

                        Notification.objects.create(
                            user_id=friend_id,
                            event=event,
                            notification_type='friend_event_reminder',
                            message=message
                        )
                        notifications_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {notifications_created} event reminder notifications'
            )
        )
