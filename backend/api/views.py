from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q

from .serializers import UserSerializer, EventSerializer, LocationSerializer
from .models import Event, Location


class EventListCreate(generics.ListCreateAPIView):
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]   # anyone can view
        return [IsAuthenticated()]  # only logged-in users can create

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Authenticated users: see public + their own events
            return Event.objects.filter(Q(is_public=True) | Q(host=user))
        # Anonymous users: only public events
        return Event.objects.filter(is_public=True)

    def perform_create(self, serializer):
        """
        ✅ Instead of forcing host=self.request.user,
        we respect `host_id` passed in the payload.
        Your EventSerializer maps host_id → host, so we
        can just call save() normally.
        """
        serializer.save()


class EventDelete(generics.DestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Only events created by the logged-in user can be deleted
        return Event.objects.filter(host=user)


# -------------------------------
# Create location safely (avoid duplicates)
# -------------------------------
# -------------------------------
# Create location safely (avoid duplicates + MultipleObjectsReturned)
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

    # Try to find an existing location first
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


@api_view(["GET"])
def location_list(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)


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
