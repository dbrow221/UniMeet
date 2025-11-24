from django.urls import path
from . import views
from .views import get_user_by_id, ProfileDetailView
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
    path("user/<int:user_id>/profile/", views.get_user_profile, name="get_user_profile"),

    # --- Location Endpoints ---
    path("locations/", views.location_list, name="location-list"),
    path("locations/create/", views.create_location, name="create-location"),

    # --- Profile Endpoint ---
    path("profile/", ProfileDetailView.as_view(), name="profile"),

    # --- Auth (JWT) ---
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


    path("friend-requests/send/<int:to_user_id>/", views.SendFriendRequestView.as_view(), name="send-friend-request"),
    path("friend-requests/received/", views.ReceivedFriendRequestsView.as_view(), name="received-friend-requests"),
    path("friend-requests/sent/", views.SentFriendRequestsView.as_view(), name="sent-friend-requests"),
    path("friend-requests/<int:pk>/accept/", views.AcceptFriendRequestView.as_view(), name="accept-friend-request"),
    path("friend-requests/<int:pk>/decline/", views.DeclineFriendRequestView.as_view(), name="decline-friend-request"),
    path("friends/", views.FriendsListView.as_view(), name="friends-list"),
    path("friends/remove/<int:friend_id>/", views.RemoveFriendView.as_view(), name="remove-friend"),
    path("users/search/", views.UserSearchView.as_view(), name="user-search"),

    # --- Messaging Endpoints ---
    path("messages/send/", views.SendMessageView.as_view(), name="send-message"),
    path("messages/conversations/", views.ConversationListView.as_view(), name="conversation-list"),
    path("messages/thread/<int:user_id>/", views.MessageThreadView.as_view(), name="message-thread"),
    path("messages/mark-read/<int:user_id>/", views.MarkMessagesReadView.as_view(), name="mark-messages-read"),

    # --- Notification Endpoints ---
    path("notifications/", views.NotificationListView.as_view(), name="notification-list"),
    path("notifications/unread-count/", views.UnreadNotificationCountView.as_view(), name="unread-notification-count"),
    path("notifications/<int:pk>/mark-read/", views.MarkNotificationReadView.as_view(), name="mark-notification-read"),
    path("notifications/mark-all-read/", views.MarkAllNotificationsReadView.as_view(), name="mark-all-notifications-read"),
]
