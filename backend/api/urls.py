from django.urls import path
from . import views
from .views import get_user_by_id



urlpatterns = [
path("events/", views.EventListCreate.as_view(), name="event-list"),
path("events/delete/<int:pk>/", views.EventDelete.as_view(), name="delete-event"),
path("user/<int:user_id>/", get_user_by_id, name="get_user_by_id"),

]