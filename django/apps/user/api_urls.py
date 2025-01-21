from django.urls import path

from .api_views import (
    UserCSRFTokenAPIView,
    UserSignupAPIView,
    UserSigninAPIView,
    UserSignoutAPIView,
    UserAPIView,
    UserGroupAPIView,
)

urlpatterns = [
    path(
        route='csrftoken/',
        view=UserCSRFTokenAPIView.as_view(),
        name='api.user.csrftoken',
    ),
    path(
        route='signup/',
        view=UserSignupAPIView.as_view(),
        name='api.user.signup',
    ),
    path(
        route='signin/',
        view=UserSigninAPIView.as_view(),
        name='api.user.signin',
    ),
    path(
        route='signout/',
        view=UserSignoutAPIView.as_view(),
        name='api.user.signout',
    ),
    path(
        route='',
        view=UserAPIView.as_view(),
        name='api.user',
    ),
    path(
        route='group/',
        view=UserGroupAPIView.as_view(),
        name='api.user.group',
    ),
]
