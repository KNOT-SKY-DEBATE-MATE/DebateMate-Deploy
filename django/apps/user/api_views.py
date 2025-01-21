from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout, authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from apps.group.models import (
    Group
)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class UserCSRFTokenAPIView(APIView):

    """
    View for csrf cookie
    """

    def get(self, request: Request):

        # Return csrf cookie
        return Response(status=200)



class UserSigninAPIView(APIView):

    """
    View for user signin
    """

    class PostSerializer(serializers.Serializer):

        # Username for user signin
        username = serializers.CharField(max_length=255, required=True)

        # Password for user signin
        password = serializers.CharField(max_length=255, required=True)

    def post(self, request: Request):

        # Get data from request
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save user
        user = authenticate(request=request, **serializer.validated_data)

        # Check if user exists
        if user is None:
            return Response(status=403)

        # Login user
        login(request=request, user=user)

        # Return token
        return Response(status=201)


class UserSignupAPIView(APIView):

    """
    View for user signup
    """

    class PostSerializer(serializers.Serializer):

        # Username for user signup
        username = serializers.CharField(max_length=255, required=True)

        # Password for user signup
        password = serializers.CharField(max_length=255, required=True)

    def post(self, request: Request):

        # Get data from request
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Chcek if user exists
        try:
            get_user_model().objects.get(username=serializer.validated_data['username'])
        except get_user_model().DoesNotExist:
            return Response(status=403)

        # Check if user exists
        user = get_user_model().objects.create_user(**serializer.validated_data)

        # Login user
        login(request=request, user=user)
        
        # Return token
        return Response(status=201)


class UserSignoutAPIView(APIView):

    """
    View for user signout
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):

        # Logout user
        logout(request)

        # Return response
        return Response(status=201)


class UserAPIView(APIView):

    """
    View for user one
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(serializers.ModelSerializer):
        
        # Serializer settings
        class Meta:
            model = get_user_model()
            fields = ['id', 'username']

    def get(self, request: Request):

        # Validate data
        serializer = self.GetOutSerializer(request.user)

        # Return user
        return Response(serializer.data)


class UserGroupAPIView(APIView):

    """
    View for user group
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(serializers.ModelSerializer):

        # Serializer settings
        class Meta:
            model = Group
            fields = '__all__'

    def get(self, request: Request):

        # Get user-groups
        groups = Group.objects.filter(groupmember__user=request.user)

        # Validate data
        out_serializer = self.GetOutSerializer(groups, many=True)

        # Return groups
        return Response(out_serializer.data)
