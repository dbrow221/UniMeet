from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from .serializers import (
    UserSerializer,
    EventSerializer,
    LocationSerializer,
    ProfileSerializer,
    JoinRequestSerializer,
    CommentSerializer, FriendRequestSerializer, UserSearchSerializer, MessageSerializer
)
from .models import Event, Location, Profile, JoinRequest, Comment, FriendRequest, Friendship, Message


# -------------------------------
# Event List + Create
# -------------------------------
class EventListCreate(generics.ListCreateAPIView):
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]  # anyone can view events
        return [IsAuthenticated()]  # must be logged in to create

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Authenticated: see all events
            queryset = Event.objects.all()
        else:
            queryset = Event.objects.filter(is_public=True)

        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        # Search by name (case-insensitive partial match)
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Filter by date (events starting on a specific date)
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(start_time__date=date)

        # We filter by location__id because the frontend will send the ID
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__id=location)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)

        return queryset.order_by('start_time')

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


# -------------------------------
# Event Detail (view only)
# -------------------------------
class EventDetail(generics.RetrieveAPIView):
    """
    Retrieve a single event by ID (read-only).
    All users (even anonymous) can view public and private events.
    """
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Event.objects.all()


# -------------------------------
# Event Update (host-only)
# -------------------------------
class EventUpdate(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        event = self.get_object()
        if event.host != self.request.user:
            raise PermissionDenied("You are not allowed to edit this event.")
        serializer.save()


# -------------------------------
# Event Delete (host-only)
# -------------------------------
class EventDelete(generics.DestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only events created by the logged-in user can be deleted
        return Event.objects.filter(host=self.request.user)


# -------------------------------
# Join Public Event
# -------------------------------
class JoinEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if event.host == user:
            return Response({"detail": "You are the host of this event."},
                            status=status.HTTP_400_BAD_REQUEST)

        if event.participant_list.filter(id=user.id).exists():
            return Response({"detail": "You already joined this event."},
                            status=status.HTTP_400_BAD_REQUEST)

        if event.is_full():
            return Response({"detail": "This event is full."},
                            status=status.HTTP_400_BAD_REQUEST)

        event.participant_list.add(user)
        return Response({"detail": "Successfully joined the event."},
                        status=status.HTTP_200_OK)


# -------------------------------
# Request to Join Private Event
# -------------------------------
class RequestJoinEventView(APIView):
    """Create a join request for a private event."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if event.is_public:
            return Response({"detail": "This is a public event. Use the join endpoint instead."},
                            status=status.HTTP_400_BAD_REQUEST)

        if event.host == user:
            return Response({"detail": "You are the host of this event."},
                            status=status.HTTP_400_BAD_REQUEST)

        if event.participant_list.filter(id=user.id).exists():
            return Response({"detail": "You are already a participant."},
                            status=status.HTTP_400_BAD_REQUEST)

        if event.is_full():
            return Response({"detail": "This event is full."},
                            status=status.HTTP_400_BAD_REQUEST)

        existing_request = JoinRequest.objects.filter(event=event, user=user).first()
        if existing_request:
            if existing_request.status == 'pending':
                return Response({"detail": "You already have a pending request."},
                                status=status.HTTP_400_BAD_REQUEST)
            elif existing_request.status == 'approved':
                return Response({"detail": "Your request was already approved."},
                                status=status.HTTP_400_BAD_REQUEST)
            elif existing_request.status == 'denied':
                existing_request.status = 'pending'
                existing_request.save()
                serializer = JoinRequestSerializer(existing_request)
                return Response(serializer.data, status=status.HTTP_200_OK)

        join_request = JoinRequest.objects.create(event=event, user=user)
        serializer = JoinRequestSerializer(join_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -------------------------------
# List Join Requests (host inbox)
# -------------------------------
class ListJoinRequestsView(generics.ListAPIView):
    """List all pending join requests for events hosted by the current user."""
    serializer_class = JoinRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JoinRequest.objects.filter(
            event__host=self.request.user,
            status='pending'
        ).select_related('event', 'user')


# -------------------------------
# Approve Join Request
# -------------------------------
class ApproveJoinRequestView(APIView):
    """Approve a join request and add user to event participants."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)

        if join_request.event.host != request.user:
            return Response({"detail": "Only the event host can approve requests."},
                            status=status.HTTP_403_FORBIDDEN)

        if join_request.status == 'approved':
            return Response({"detail": "This request has already been approved."},
                            status=status.HTTP_400_BAD_REQUEST)

        if join_request.event.is_full():
            return Response({"detail": "This event is now full."},
                            status=status.HTTP_400_BAD_REQUEST)

        join_request.status = 'approved'
        join_request.save()
        join_request.event.participant_list.add(join_request.user)

        serializer = JoinRequestSerializer(join_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------------
# Deny Join Request
# -------------------------------
class DenyJoinRequestView(APIView):
    """Deny a join request."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)

        if join_request.event.host != request.user:
            return Response({"detail": "Only the event host can deny requests."},
                            status=status.HTTP_403_FORBIDDEN)

        if join_request.status == 'denied':
            return Response({"detail": "This request has already been denied."},
                            status=status.HTTP_400_BAD_REQUEST)

        join_request.status = 'denied'
        join_request.save()

        serializer = JoinRequestSerializer(join_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------------
# Leave Event
# -------------------------------
class LeaveEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if not event.participant_list.filter(id=user.id).exists():
            return Response({"detail": "You are not part of this event."},
                            status=status.HTTP_400_BAD_REQUEST)

        event.participant_list.remove(user)
        return Response({"detail": "Successfully left the event."},
                        status=status.HTTP_200_OK)


# -------------------------------
# Hosted / Joined Events
# -------------------------------
class HostedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(host=self.request.user).order_by("-start_time")


class JoinedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(participant_list=self.request.user).order_by("-start_time")


# -------------------------------
# Location Create / List
# -------------------------------
@api_view(["POST"])
def create_location(request):
    name = request.data.get("name")
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    if not (name and latitude is not None and longitude is not None):
        return Response({"error": "name, latitude, and longitude are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    location = Location.objects.filter(name=name, latitude=latitude, longitude=longitude).first()

    if not location:
        location = Location.objects.create(name=name, latitude=latitude, longitude=longitude)
        status_code = status.HTTP_201_CREATED
    else:
        status_code = status.HTTP_200_OK

    serializer = LocationSerializer(location)
    return Response(serializer.data, status=status_code)


@api_view(["GET"])
@permission_classes([AllowAny])
def location_list(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)


# -------------------------------
#  User Creation + Profile Management
# -------------------------------
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile = request.user.profile  # Assumes profile is created on user creation

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Fetch user info by ID
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return Response({"id": user.id, "username": user.username})
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request, user_id):
    """Get public profile information for any user."""
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)

        # Check if they are friends
        current_user = request.user
        user1, user2 = (current_user, user) if current_user.id < user.id else (user, current_user)
        is_friend = Friendship.objects.filter(user1=user1, user2=user2).exists()
        
        # Check friend request status
        friend_request_status = None
        friend_request = FriendRequest.objects.filter(
            Q(from_user=current_user, to_user=user) |
            Q(from_user=user, to_user=current_user)
        ).first()
        
        if friend_request:
            if friend_request.from_user == current_user:
                friend_request_status = f"sent_{friend_request.status}"
            else:
                friend_request_status = f"received_{friend_request.status}"
        
        return Response({
            "id": user.id,
            "username": user.username,
            "bio": profile.bio,
            "location": profile.location,
            "pronouns": profile.pronouns,
            "profile_picture": profile.profile_picture,
            "is_friend": is_friend,
            "friend_request_status": friend_request_status,
        })
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------
# Comments (Event-specific)
# -------------------------------
class EventCommentListCreate(generics.ListCreateAPIView):
    """List and create comments for a specific event."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Comment.objects.filter(event_id=event_id).select_related('user')

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, pk=event_id)
        serializer.save(user=self.request.user, event=event)

# -------------------------------
# Friend Requests
# -------------------------------        

class FriendRequestView(generics.CreateAPIView):
    """Create a friend request."""
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        to_user_id = self.request.data.get("to_user_id")
        to_user = get_object_or_404(User, pk=to_user_id)

        if to_user == self.request.user:
            raise PermissionDenied("You cannot send a friend request to yourself.")

        existing_request = FriendRequest.objects.filter(
            Q(from_user=self.request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=self.request.user)
        ).first()

        if existing_request:
            if existing_request.status == 'pending':
                raise PermissionDenied("A friend request is already pending.")
            elif existing_request.status == 'approved':
                raise PermissionDenied("You are already friends.")
            elif existing_request.status == 'denied':
                existing_request.status = 'pending'
                existing_request.save()
                return

        serializer.save(from_user=self.request.user, to_user=to_user)


class AcceptFriendRequestView(generics.UpdateAPIView):
    """Accept a pending friend request and create a friendship."""
    queryset = FriendRequest.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()

        if friend_request.to_user != request.user:
            raise PermissionDenied("You are not authorized to accept this friend request.")

        if friend_request.status != 'pending':
            raise PermissionDenied("This friend request has already been processed.")

        friend_request.status = 'accepted'
        friend_request.save(update_fields=['status'])

        # Create bidirectional friendship (ensure user1 id is always smaller than user2 id)
        user1 = friend_request.from_user
        user2 = friend_request.to_user
        
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        # Create friendship if it doesn't already exist
        Friendship.objects.get_or_create(user1=user1, user2=user2)

        return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)
    

class DeclineFriendRequestView(generics.UpdateAPIView):
    """Decline a pending friend request."""
    queryset = FriendRequest.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()

        if friend_request.to_user != request.user:
            raise PermissionDenied("You are not authorized to decline this friend request.")

        if friend_request.status != 'pending':
            raise PermissionDenied("This friend request has already been processed.")

        friend_request.status = 'denied'
        friend_request.save(update_fields=['status'])

        return Response({"detail": "Friend request declined."}, status=status.HTTP_200_OK)
    
class FriendsListView(generics.ListAPIView):
    """List all accepted friends for the current user."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        # Get friends from Friendship model - friends can be in either user1 or user2 position
        friend_ids = set()
        
        # Get friendships where current user is user1
        friendships_as_user1 = Friendship.objects.filter(user1=user).values_list('user2_id', flat=True)
        friend_ids.update(friendships_as_user1)
        
        # Get friendships where current user is user2
        friendships_as_user2 = Friendship.objects.filter(user2=user).values_list('user1_id', flat=True)
        friend_ids.update(friendships_as_user2)
        
        return User.objects.filter(id__in=friend_ids)
    
class SendFriendRequestView(APIView):
    """Send a friend request to another user."""
    permission_classes = [IsAuthenticated]

    def post(self, request, to_user_id):
        to_user = get_object_or_404(User, pk=to_user_id)

        if to_user == request.user:
            return Response(
                {"detail": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing requests in either direction
        existing_request = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()

        if existing_request:
            if existing_request.status == 'pending':
                return Response(
                    {"detail": "A friend request is already pending."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif existing_request.status == 'accepted':
                return Response(
                    {"detail": "You are already friends."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif existing_request.status == 'declined':
                # Resend by updating the declined request
                existing_request.status = 'pending'
                existing_request.from_user = request.user
                existing_request.to_user = to_user
                existing_request.save()
                serializer = FriendRequestSerializer(existing_request)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # Create new friend request
        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=to_user
        )
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReceivedFriendRequestsView(generics.ListAPIView):
    """List all pending friend requests received by the user."""
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')


class SentFriendRequestsView(generics.ListAPIView):
    """List all pending friend requests sent by the user."""
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(from_user=self.request.user, status='pending')


class RemoveFriendView(APIView):
    """Remove a friend (delete friendship and update friend request status)."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, friend_id):
        friend = get_object_or_404(User, pk=friend_id)
        user = request.user

        if friend == user:
            return Response(
                {"detail": "You cannot remove yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find and delete the friendship (could be in either direction)
        user1, user2 = (user, friend) if user.id < friend.id else (friend, user)
        friendship = Friendship.objects.filter(user1=user1, user2=user2).first()

        if not friendship:
            return Response(
                {"detail": "You are not friends with this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete the friendship
        friendship.delete()

        # Update the friend request status to declined (if exists)
        friend_request = FriendRequest.objects.filter(
            Q(from_user=user, to_user=friend) | Q(from_user=friend, to_user=user),
            status='accepted'
        ).first()

        if friend_request:
            friend_request.status = 'declined'
            friend_request.save()

        return Response(
            {"detail": "Friend removed successfully."},
            status=status.HTTP_200_OK
        )


# views.py
from django.contrib.auth.models import User
from rest_framework import generics, permissions, serializers

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserSearchView(generics.ListAPIView):
    """Search users by username (case-insensitive partial match)."""
    serializer_class = UserSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return User.objects.filter(username__icontains=query).exclude(id=self.request.user.id)
        return User.objects.none()


# -------------------------------
# Messaging
# -------------------------------

class SendMessageView(generics.CreateAPIView):
    """Send a message to another user."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ConversationListView(APIView):
    """Get list of users the current user has conversations with."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get all users who have sent or received messages from/to current user
        sent_to = Message.objects.filter(sender=user).values_list('recipient_id', flat=True).distinct()
        received_from = Message.objects.filter(recipient=user).values_list('sender_id', flat=True).distinct()
        
        conversation_user_ids = set(sent_to) | set(received_from)
        users = User.objects.filter(id__in=conversation_user_ids)
        
        # Get last message and unread count for each conversation
        conversations = []
        for other_user in users:
            # Get last message between users
            last_message = Message.objects.filter(
                Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
            ).order_by('-created_at').first()
            
            # Count unread messages from other user
            unread_count = Message.objects.filter(
                sender=other_user,
                recipient=user,
                read=False
            ).count()
            
            conversations.append({
                'user': {
                    'id': other_user.id,
                    'username': other_user.username
                },
                'last_message': {
                    'content': last_message.content if last_message else '',
                    'created_at': last_message.created_at if last_message else None,
                    'sender_id': last_message.sender_id if last_message else None
                } if last_message else None,
                'unread_count': unread_count
            })
        
        # Sort by last message time
        conversations.sort(key=lambda x: x['last_message']['created_at'] if x['last_message'] else '', reverse=True)
        
        return Response(conversations)


class MessageThreadView(generics.ListAPIView):
    """Get all messages between current user and another user."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        other_user_id = self.kwargs.get('user_id')
        user = self.request.user
        
        # Get messages between the two users
        messages = Message.objects.filter(
            Q(sender=user, recipient_id=other_user_id) |
            Q(sender_id=other_user_id, recipient=user)
        ).order_by('created_at')
        
        return messages


class MarkMessagesReadView(APIView):
    """Mark all messages from a specific user as read."""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from django.utils import timezone
        
        messages = Message.objects.filter(
            sender_id=user_id,
            recipient=request.user,
            read=False
        )
        
        count = messages.update(read=True, read_at=timezone.now())
        
        return Response({
            "detail": f"Marked {count} messages as read."
        }, status=status.HTTP_200_OK)


# -------------------------------
# Notifications
# -------------------------------

from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    """List all notifications for the current user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class UnreadNotificationCountView(APIView):
    """Get count of unread notifications."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})


class MarkNotificationReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.utils import timezone
        
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)


class MarkAllNotificationsReadView(APIView):
    """Mark all notifications as read for the current user."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.utils import timezone
        
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({
            "detail": f"Marked {count} notifications as read."
        }, status=status.HTTP_200_OK)
