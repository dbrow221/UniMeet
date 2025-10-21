from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import permissions, generics
from rest_framework.exceptions import PermissionDenied 

from .serializers import UserSerializer, EventSerializer, LocationSerializer, JoinRequestSerializer, CommentSerializer
from .models import Event, Location, JoinRequest, Comment


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
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Everyone can view both public and private events
        return Event.objects.all()

# -------------------------------
# Event Update (host-only)
# -------------------------------
class EventUpdate(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        # Optional: only allow hosts to edit their own events
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
# Join Event
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
                existing_request.status = 'pending'
                existing_request.save()
                serializer = JoinRequestSerializer(existing_request)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # Create new join request
        join_request = JoinRequest.objects.create(event=event, user=user)
        serializer = JoinRequestSerializer(join_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -------------------------------
# List Join Requests (for Inbox)
# -------------------------------
class ListJoinRequestsView(generics.ListAPIView):
    """List all pending join requests for events hosted by the current user."""
    serializer_class = JoinRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all pending requests for events hosted by current user
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
# Hosted Events (by current user)
# -------------------------------
class HostedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(host=self.request.user).order_by("-start_time")


# -------------------------------
# Joined Events (by current user)
# -------------------------------
class JoinedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(participant_list=self.request.user).order_by("-start_time")


# -------------------------------
# Create Location Safely
# -------------------------------
@api_view(["POST"])
def create_location(request):
    name = request.data.get("name")
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    if not (name and latitude is not None and longitude is not None):
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
        status_code = status.HTTP_201_CREATED
    else:
        status_code = status.HTTP_200_OK

    serializer = LocationSerializer(location)
    return Response(serializer.data, status=status_code)


# -------------------------------
# List Locations
# -------------------------------
@api_view(["GET"])
def location_list(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)


# -------------------------------
# Create User
# -------------------------------
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


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
        return Response(
            {"detail": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# -------------------------------
# Comments
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
