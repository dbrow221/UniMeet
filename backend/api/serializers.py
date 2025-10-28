from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Event, Location, Profile, JoinRequest, Comment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone


# --- USER SERIALIZERS ---

class UserSerializer(serializers.ModelSerializer):
    # for user registration and updates
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def update(self, instance, validated_data):
        # handling for password change
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def create(self, validated_data):
        # automatically hashes the password
        user = User.objects.create_user(**validated_data)
        return user
    
class NestedUserSerializer(serializers.ModelSerializer):
    # for updating username/password within ProfileSerializer
    class Meta:
        model = User
        fields = ["username", "password"]
        # do NOT require username/password for profile updates
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "username": {"required": False},
        }

    def update(self, instance, validated_data):
        # Only update fields that are actually passed in
        username = validated_data.get("username", None)
        password = validated_data.get("password", None)

        if username is not None:
            instance.username = username

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class SafeUserSerializer(serializers.ModelSerializer):
    # for displaying user data safely (no password)
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

    def validate(self, data):
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))

        if start and end and end <= start:
            raise serializers.ValidationError("End time must be after start time.")

        if data.get("start_time") and data["start_time"] < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past.")

        return data

    def create(self, validated_data):
        """Ensure the event host is the authenticated user."""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["host"] = request.user
        return Event.objects.create(**validated_data)


# --- PROFILE SERIALIZER ---

class ProfileSerializer(serializers.ModelSerializer):
    # for user profile details and updates
    user = NestedUserSerializer(required=False)
    bio = serializers.CharField(allow_blank=True, required=False)
    location = serializers.CharField(allow_blank=True, required=False)
    pronouns = serializers.CharField(allow_blank=True, required=False)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "user",  # nested user for username/password updates
            "bio",
            "location",
            "pronouns",
            "notifications_enabled",
        ]

    def update(self, instance, validated_data):
        # Extract nested user info if included
        user_data = validated_data.pop("user", None)

        if user_data:
            user = instance.user
            username = user_data.get("username")
            password = user_data.get("password")

            # Update user fields if provided, otherwise leave unchanged
            if username:
                user.username = username
            if password:
                user.set_password(password)
            user.save()

        # Update profile-specific fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        # include username at top level of representation for convenience
        rep = super().to_representation(instance)
        rep["username"] = instance.user.username
        return rep


# --- JOIN REQUEST SERIALIZER ---

class JoinRequestSerializer(serializers.ModelSerializer):
    """Serializer for join requests to private events."""
    
    event_details = EventSerializer(source="event", read_only=True)
    user_details = SafeUserSerializer(source="user", read_only=True)
    
    class Meta:
        model = JoinRequest
        fields = [
            "id",
            "event",
            "user",
            "status",
            "created_at",
            "updated_at",
            "event_details",
            "user_details",
        ]
        read_only_fields = ["created_at", "updated_at", "status"]


# --- COMMENT SERIALIZER ---

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for event comments."""
    
    user_details = SafeUserSerializer(source="user", read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            "id",
            "event",
            "user",
            "text",
            "created_at",
            "updated_at",
            "user_details",
        ]
        read_only_fields = ["created_at", "updated_at", "user"]
    
    def create(self, validated_data):
        """Ensure the comment user is the authenticated user."""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return Comment.objects.create(**validated_data)
