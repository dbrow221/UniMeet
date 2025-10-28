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
    CommentSerializer
)
from .models import Event, Location, Profile, JoinRequest, Comment


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
            return Event.objects.all()
        return Event.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


# -------------------------------
# Event Detail (view only)
# -------------------------------
class EventDetail(generics.RetrieveAPIView):
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


# -------------------------------
# Comments (Event-specific)
# -------------------------------
class EventCommentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Comment.objects.filter(event_id=event_id).select_related('user')

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, pk=event_id)
        serializer.save(user=self.request.user, event=event)
