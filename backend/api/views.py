from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
<<<<<<< HEAD
from rest_framework import generics, status, permissions
=======
from rest_framework import generics, status
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
<<<<<<< HEAD
from rest_framework.exceptions import PermissionDenied 

from .serializers import (
    UserSerializer,
    EventSerializer,
    LocationSerializer,
    ProfileSerializer,
    JoinRequestSerializer,
    CommentSerializer
)
from .models import Event, Location, Profile, JoinRequest, Comment
=======
from rest_framework import permissions, generics
from rest_framework.exceptions import PermissionDenied 

from .serializers import UserSerializer, EventSerializer, LocationSerializer, JoinRequestSerializer, CommentSerializer
from .models import Event, Location, JoinRequest, Comment
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e


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
<<<<<<< HEAD
            return Event.objects.all()
        return Event.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


# -------------------------------
# Event Detail (view only)
# -------------------------------
class EventDetail(generics.RetrieveAPIView):
=======
            return Event.objects

    def perform_create(self, serializer):
        # Host is automatically set in the serializer (from request.user)
        serializer.save()



class EventDetail(generics.RetrieveAPIView):
    """
    Retrieve a single event by ID (read-only).
    All users (even anonymous) can view public and private events.
    However, only hosts or participants can join/edit private events.
    """
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
<<<<<<< HEAD
        return Event.objects.all()


=======
        # Everyone can view both public and private events
        return Event.objects.all()

>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
# -------------------------------
# Event Update (host-only)
# -------------------------------
class EventUpdate(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
<<<<<<< HEAD
=======
        # Optional: only allow hosts to edit their own events
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
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
<<<<<<< HEAD
=======
        # Only events created by the logged-in user can be deleted
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
        return Event.objects.filter(host=self.request.user)


# -------------------------------
<<<<<<< HEAD
# Join Public Event
=======
# Join Event
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
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
<<<<<<< HEAD

=======
    
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e

# -------------------------------
# Request to Join Private Event
# -------------------------------
class RequestJoinEventView(APIView):
<<<<<<< HEAD
=======
    """Create a join request for a private event."""
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

<<<<<<< HEAD
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
=======
        # Check if event is public (no need to request)
        if event.is_public:
            return Response(
                {"detail": "This is a public event. Use the join endpoint instead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is the host
        if event.host == user:
            return Response(
                {"detail": "You are the host of this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is already a participant
        if event.participant_list.filter(id=user.id).exists():
            return Response(
                {"detail": "You are already a participant in this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if event is full
        if event.is_full():
            return Response(
                {"detail": "This event is full."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a request already exists
        existing_request = JoinRequest.objects.filter(event=event, user=user).first()
        if existing_request:
            if existing_request.status == 'pending':
                return Response(
                    {"detail": "You already have a pending request for this event."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif existing_request.status == 'approved':
                return Response(
                    {"detail": "Your request was already approved."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif existing_request.status == 'denied':
                # Allow resubmission if previously denied
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
                existing_request.status = 'pending'
                existing_request.save()
                serializer = JoinRequestSerializer(existing_request)
                return Response(serializer.data, status=status.HTTP_200_OK)

<<<<<<< HEAD
=======
        # Create new join request
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
        join_request = JoinRequest.objects.create(event=event, user=user)
        serializer = JoinRequestSerializer(join_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -------------------------------
<<<<<<< HEAD
# List Join Requests (host inbox)
# -------------------------------
class ListJoinRequestsView(generics.ListAPIView):
=======
# List Join Requests (for Inbox)
# -------------------------------
class ListJoinRequestsView(generics.ListAPIView):
    """List all pending join requests for events hosted by the current user."""
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
    serializer_class = JoinRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
<<<<<<< HEAD
=======
        # Get all pending requests for events hosted by current user
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
        return JoinRequest.objects.filter(
            event__host=self.request.user,
            status='pending'
        ).select_related('event', 'user')


# -------------------------------
# Approve Join Request
# -------------------------------
class ApproveJoinRequestView(APIView):
<<<<<<< HEAD
=======
    """Approve a join request and add user to event participants."""
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)
<<<<<<< HEAD

        if join_request.event.host != request.user:
            return Response({"detail": "Only the event host can approve requests."},
                            status=status.HTTP_403_FORBIDDEN)

        if join_request.status == 'approved':
            return Response({"detail": "This request has already been approved."},
                            status=status.HTTP_400_BAD_REQUEST)

        if join_request.event.is_full():
            return Response({"detail": "This event is now full."},
                            status=status.HTTP_400_BAD_REQUEST)

=======
        
        # Verify the current user is the event host
        if join_request.event.host != request.user:
            return Response(
                {"detail": "Only the event host can approve requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already approved
        if join_request.status == 'approved':
            return Response(
                {"detail": "This request has already been approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if event is full
        if join_request.event.is_full():
            return Response(
                {"detail": "This event is now full."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Approve the request and add user to participants
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
        join_request.status = 'approved'
        join_request.save()
        join_request.event.participant_list.add(join_request.user)

        serializer = JoinRequestSerializer(join_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------------
# Deny Join Request
# -------------------------------
class DenyJoinRequestView(APIView):
<<<<<<< HEAD
=======
    """Deny a join request."""
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)
<<<<<<< HEAD

        if join_request.event.host != request.user:
            return Response({"detail": "Only the event host can deny requests."},
                            status=status.HTTP_403_FORBIDDEN)

        if join_request.status == 'denied':
            return Response({"detail": "This request has already been denied."},
                            status=status.HTTP_400_BAD_REQUEST)

=======
        
        # Verify the current user is the event host
        if join_request.event.host != request.user:
            return Response(
                {"detail": "Only the event host can deny requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already denied
        if join_request.status == 'denied':
            return Response(
                {"detail": "This request has already been denied."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deny the request
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
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
<<<<<<< HEAD
# Hosted / Joined Events
=======
# Hosted Events (by current user)
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
# -------------------------------
class HostedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(host=self.request.user).order_by("-start_time")


<<<<<<< HEAD
=======
# -------------------------------
# Joined Events (by current user)
# -------------------------------
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
class JoinedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(participant_list=self.request.user).order_by("-start_time")


# -------------------------------
<<<<<<< HEAD
# Location Create / List
=======
# Create Location Safely
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
# -------------------------------
@api_view(["POST"])
def create_location(request):
    name = request.data.get("name")
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    if not (name and latitude is not None and longitude is not None):
<<<<<<< HEAD
        return Response({"error": "name, latitude, and longitude are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    location = Location.objects.filter(name=name, latitude=latitude, longitude=longitude).first()

    if not location:
        location = Location.objects.create(name=name, latitude=latitude, longitude=longitude)
=======
        return Response(
            {"error": "name, latitude, and longitude are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    location = Location.objects.filter(
        name=name,
        latitude=latitude,
        longitude=longitude,
    ).first()

    if not location:
        location = Location.objects.create(
            name=name,
            latitude=latitude,
            longitude=longitude,
        )
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
        status_code = status.HTTP_201_CREATED
    else:
        status_code = status.HTTP_200_OK

    serializer = LocationSerializer(location)
    return Response(serializer.data, status=status_code)


<<<<<<< HEAD
=======
# -------------------------------
# List Locations
# -------------------------------
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
@api_view(["GET"])
def location_list(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)


# -------------------------------
<<<<<<< HEAD
#  User Creation + Profile Management
=======
# Create User
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
# -------------------------------
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


<<<<<<< HEAD
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile = request.user.profile # Assumes profile is created on user creation

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


=======
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
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
<<<<<<< HEAD
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------
# Comments (Event-specific)
# -------------------------------
class EventCommentListCreate(generics.ListCreateAPIView):
=======
        return Response(
            {"detail": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# -------------------------------
# Comments
# -------------------------------
class EventCommentListCreate(generics.ListCreateAPIView):
    """List and create comments for a specific event."""
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Comment.objects.filter(event_id=event_id).select_related('user')

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, pk=event_id)
        serializer.save(user=self.request.user, event=event)
