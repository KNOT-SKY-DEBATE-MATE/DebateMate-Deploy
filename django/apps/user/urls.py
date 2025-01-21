from django.urls import path

from .views import (
    UserLoginView,
    UserView,
)


urlpatterns = [
    path(
        route='login/',
        view=UserLoginView.as_view(),
        name='user.login',
    ),
    path(
        route='',
        view=UserView.as_view(),
        name='user',
    ),
]
