from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Event, Location
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","password"]
        extra_kwargs = {"password": {"write_only": True}}


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user 
    


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "address", "latitude", "longitude"]
    


class EventSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source="location", write_only=True
    )

    class Meta:
        model = Event
        fields = ["id", "name", "details", "posted_date", "host", "location", "location_id", "is_public"]
        extra_kwargs = {"host": {"read_only": True}}
    






