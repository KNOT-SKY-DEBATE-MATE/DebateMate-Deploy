from django.urls import path, include
from allauth.account.views import LoginView
from allauth.socialaccount.views import SignupView, LoginCancelledView, LoginErrorView

from .views import (
    UserAuthenticationView,
    UserView,
)


urlpatterns = [
    path(
        route='authentication/',
        view=UserAuthenticationView.as_view(),
        name='user.authentication',
    ),
    path(
        route='',
        view=UserView.as_view(),
        name='user',
    ),
]
