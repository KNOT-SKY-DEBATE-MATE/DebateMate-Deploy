from django.urls import path

from .api_views import (
    MeetingAPIView,
    MeetingOneAPIView,
    MeetingMemberAPIView,
    MeetingMemberKickAPIView,
    MeetingMessageAPIView,
    MeetingMessageOneAPIView,
    MeetingMessageAnnotationAPIView,
)

urlpatterns = [
    path(
        route='',
        view=MeetingAPIView.as_view(),
        name='api.meeting',
    ),
    path(
        route='<uuid:meeting_id>/',
        view=MeetingOneAPIView.as_view(),
        name='api.meeting.(id)',
    ),
    path(
        route='<uuid:meeting_id>/member/',
        view=MeetingMemberAPIView.as_view(),
        name='api.meeting.(id).member',
    ),
    path(
        route='<uuid:meeting_id>/member/kick/',
        view=MeetingMemberKickAPIView.as_view(),
        name='api.meeting.(id).member.kick',
    ),
    path(
        route='<uuid:meeting_id>/message/',
        view=MeetingMessageAPIView.as_view(),
        name='api.meeting.(id).message',
    ),
    path(
        route='<uuid:meeting_id>/message/<uuid:message_id>/',
        view=MeetingMessageOneAPIView.as_view(),
        name='api.meeting.(id).message.(id)',
    ),
    path(
        route='<uuid:meeting_id>/message/<uuid:message_id>/annotation/',
        view=MeetingMessageAnnotationAPIView.as_view(),
        name='api.meeting.(id).message.(id).annotation',
    ),

]
