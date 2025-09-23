from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Event, Location
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    # Read-only nested objects for frontend
    location_details = LocationSerializer(source="location", read_only=True)
    host_details = UserSerializer(source="host", read_only=True)

    # Write-only IDs for creation
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="location",
        write_only=True
    )
    host_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="host",
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
            "location_details",
            "host_details",
            "location_id",
            "host_id",
        ]

    def create(self, validated_data):
        """
        Create Event instance using validated_data.
        'location' and 'host' are set via location_id and host_id automatically.
        """
        return Event.objects.create(**validated_data)
