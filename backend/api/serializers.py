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
    # Read-only nested details
    location = LocationSerializer(read_only=True)
    host = UserSerializer(read_only=True)

    # Write-only IDs
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
        fields = "__all__"

    def create(self, validated_data):
        return Event.objects.create(**validated_data)
