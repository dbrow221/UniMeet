from django.urls import path
from . import views
from .views import get_user_by_id

urlpatterns = [
    # Events
    path("events/", views.EventListCreate.as_view(), name="event-list"),
    path("events/delete/<int:pk>/", views.EventDelete.as_view(), name="delete-event"),

    # User
    path("user/<int:user_id>/", get_user_by_id, name="get_user_by_id"),

    # Locations
    path("locations/", views.location_list, name="location-list"),       # GET list of locations
    path("locations/create/", views.create_location, name="create-location"),  # POST to create
]
