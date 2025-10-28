from django.urls import path
from . import views
<<<<<<< HEAD
from .views import get_user_by_id, ProfileDetailView
=======
from .views import get_user_by_id
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # --- Event Endpoints ---
    path("events/", views.EventListCreate.as_view(), name="event-list"),
    path("events/<int:pk>/", views.EventDetail.as_view(), name="event-detail"),
    path("events/delete/<int:pk>/", views.EventDelete.as_view(), name="delete-event"),
    path("events/<int:pk>/join/", views.JoinEventView.as_view(), name="join-event"),
    path("events/<int:pk>/request-join/", views.RequestJoinEventView.as_view(), name="request-join-event"),
    path("events/<int:pk>/leave/", views.LeaveEventView.as_view(), name="leave-event"),
    path("events/hosted/", views.HostedEventsView.as_view(), name="hosted-events"),
    path("events/joined/", views.JoinedEventsView.as_view(), name="joined-events"),
    path("events/edit/<int:pk>/", views.EventUpdate.as_view(), name="edit-event"),
    
    # --- Join Request Endpoints ---
    path("join-requests/", views.ListJoinRequestsView.as_view(), name="list-join-requests"),
    path("join-requests/<int:pk>/approve/", views.ApproveJoinRequestView.as_view(), name="approve-join-request"),
    path("join-requests/<int:pk>/deny/", views.DenyJoinRequestView.as_view(), name="deny-join-request"),
    
    # --- Comment Endpoints ---
    path("events/<int:event_id>/comments/", views.EventCommentListCreate.as_view(), name="event-comments"),

    # --- User Endpoints ---
    path("user/<int:user_id>/", get_user_by_id, name="get_user_by_id"),

    # --- Location Endpoints ---
    path("locations/", views.location_list, name="location-list"),
    path("locations/create/", views.create_location, name="create-location"),

<<<<<<< HEAD
    # --- Profile Endpoint ---
    path("profile/", ProfileDetailView.as_view(), name="profile"),

=======
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
    # --- Auth (JWT) ---
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
