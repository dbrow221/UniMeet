from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Event, Location
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone


# --- USER SERIALIZERS ---

class UserSerializer(serializers.ModelSerializer):
    """Used only for user registration (write-only password)."""
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Automatically hashes the password."""
        user = User.objects.create_user(**validated_data)
        return user


class SafeUserSerializer(serializers.ModelSerializer):
    """Used for displaying user data safely (no password)."""
    class Meta:
        model = User
        fields = ["id", "username"]


# --- LOCATION SERIALIZER ---

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


# --- EVENT SERIALIZER ---

class EventSerializer(serializers.ModelSerializer):
    """Handles safe event serialization and creation."""
    
    # Read-only nested details for frontend display
    location_details = LocationSerializer(source="location", read_only=True)
    host_details = SafeUserSerializer(source="host", read_only=True)
    participant_list = SafeUserSerializer(many=True, read_only=True)

    # Write-only IDs for linking
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="location",
        write_only=True
    )

    # host_id removed for security (host auto-set from request.user)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "details",
            "posted_date",
            "is_public",
            "start_time",
            "end_time",
            "max_capacity",
            "participant_list",
            "location_details",
            "host_details",
            "location_id",
        ]
        read_only_fields = ["posted_date"]

    # --- Validation logic ---
    def validate(self, data):
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))

        if start and end and end <= start:
            raise serializers.ValidationError("End time must be after start time.")

        if data.get("start_time") and data["start_time"] < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past.")

        return data

    # --- Creation logic ---
    def create(self, validated_data):
        """Ensure the event host is the authenticated user."""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["host"] = request.user
        return Event.objects.create(**validated_data)
