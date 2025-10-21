from django.urls import path
from . import views
from .views import get_user_by_id
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # --- Event Endpoints ---
    path("events/", views.EventListCreate.as_view(), name="event-list"),
    path("events/<int:pk>/", views.EventDetail.as_view(), name="event-detail"),
    path("events/delete/<int:pk>/", views.EventDelete.as_view(), name="delete-event"),
    path("events/<int:pk>/join/", views.JoinEventView.as_view(), name="join-event"),
    path("events/<int:pk>/leave/", views.LeaveEventView.as_view(), name="leave-event"),
    path("events/hosted/", views.HostedEventsView.as_view(), name="hosted-events"),
    path("events/joined/", views.JoinedEventsView.as_view(), name="joined-events"),

    # --- User Endpoints ---
    path("user/<int:user_id>/", get_user_by_id, name="get_user_by_id"),

    # --- Location Endpoints ---
    path("locations/", views.location_list, name="location-list"),
    path("locations/create/", views.create_location, name="create-location"),

    # --- Auth (JWT) ---
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
