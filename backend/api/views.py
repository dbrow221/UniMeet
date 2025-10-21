from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView

from .serializers import UserSerializer, EventSerializer, LocationSerializer
from .models import Event, Location


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
            # Authenticated: see public events + own events
            return Event.objects.filter(Q(is_public=True) | Q(host=user))
        # Anonymous: only public events
        return Event.objects.filter(is_public=True)

    def perform_create(self, serializer):
        # Host is automatically set in the serializer (from request.user)
        serializer.save()



class EventDetail(generics.RetrieveAPIView):
    """
    Retrieve a single event by ID (read-only).
    Public events visible to anyone.
    Private events visible only to host or participants.
    """
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Event.objects.filter(Q(is_public=True) | Q(host=user) | Q(participant_list=user))
        return Event.objects.filter(is_public=True)

# -------------------------------
# Event Update (host-only)
# -------------------------------
class EventUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Hosts can only update their own events
        return Event.objects.filter(host=self.request.user)


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
