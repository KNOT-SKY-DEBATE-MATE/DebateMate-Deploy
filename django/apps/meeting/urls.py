# apps/meeting/urls.py
from django.urls import path
from .views import MeetingView, MeetingVideoView

from .views import (
    MeetingView,
)

urlpatterns = [
    path(
        route='<uuid:meeting_id>/',
        view=MeetingView.as_view(),
        name='meeting.(id)',
    ),
    path(
        route='<uuid:meeting_id>/video/',
        view=MeetingVideoView.as_view(), 
        name='meeting.(id).video',
    ),
]