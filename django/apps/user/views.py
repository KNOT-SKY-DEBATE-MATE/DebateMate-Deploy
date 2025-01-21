# apps/user/views.py
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest


class UserLoginView(View):

    """
    View for user authentication
    """

    def get(self, request: HttpRequest):

        # Return authentication page
        return render(request, 'user-login.html')


class UserView(LoginRequiredMixin, View):

    """
    View for user
    """

    def get(self, request: HttpRequest):

        # Render dashboard
        return render(request, 'user.html', {'user': request.user})
