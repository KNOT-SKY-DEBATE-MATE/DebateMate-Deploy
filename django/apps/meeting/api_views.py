# apps/meeting/api_views.py
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.group.models import (
    GroupMember,
)

from .models import (
    Meeting,
    MeetingMember,
    MeetingMessage,
    MeetingMessageAnnotation,
)

from .serializers import (
    MeetingSerializer,
    MeetingMemberSerializer,
    MeetingMessageSerializer,
    MeetingMessageAnnotationSerializer
)


class MeetingAPIView(APIView):

    """
    List all meetings, or create a new meeting.    
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(MeetingSerializer):
        class Meta(MeetingSerializer.Meta):
            depth = 1

    def get(self, request: Request):
        """
        List all meetings.
        """

        # Get group
        meetings = Meeting.objects.all()

        # Validate data
        out_serializer = self.GetOutSerializer(meetings, many=True)

        # Return group
        return Response(out_serializer.data)

    class PostSerializer(MeetingSerializer):
        class Meta(MeetingSerializer.Meta):
            fields = ['title', 'group', 'description']

    class PostOutSerializer(MeetingSerializer):
        class Meta(MeetingSerializer.Meta):
            depth = 1

    def post(self, request: Request):
        """
        Create a new meeting.
        """

        # Get data from request
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not GroupMember.objects\
                .filter(group=serializer.validated_data['group'], user=request.user)\
                .exists():
            return Response(status=403)
        
        # Save meeting
        meeting = serializer.save()

        # Save meeting-member
        MeetingMember.objects.create(meeting=meeting, user=request.user)

        # Validate data
        out_serializer = self.PostOutSerializer(meeting)

        # Return meeting
        return Response(out_serializer.data)


class MeetingOneAPIView(APIView):

    """
    Retrieve, update or delete a meeting.    
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(MeetingSerializer):
        class Meta(MeetingSerializer.Meta):
            depth = 1

    def get(self, request: Request, meeting_id):
        """
        Retrieve a meeting.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        if not MeetingMember.objects\
                .filter(meeting=meeting, user=request.user, is_kicked=False)\
                .exists():
            return Response(status=403)

        # Validate data
        out_serializer = self.GetOutSerializer(meeting)

        # Return meeting
        return Response(out_serializer.data)
    
    class PatchSerializer(MeetingSerializer):
        class Meta(MeetingSerializer.Meta):
            fields = ['title', 'description']

    class PatchOutSerializer(MeetingSerializer):
        class Meta(MeetingSerializer.Meta):
            depth = 1

    def patch(self, request: Request, meeting_id):
        """
        Update a meeting.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any group
        if not MeetingMember.objects\
                .filter(meeting=meeting, user=request.user, is_kicked=False)\
                .exists():
            return Response(status=403)

        # Get data from request
        serializer = self.PatchSerializer(meeting, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save meeting
        meeting = serializer.save()

        # Validate data
        out_serializer = self.PatchOutSerializer(meeting)

        # Return meeting
        return Response(out_serializer.data)


class MeetingMemberAPIView(APIView):

    """
    List all meeting members, or create a new meeting member.
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(MeetingMemberSerializer):
        class Meta(MeetingMemberSerializer.Meta):
            depth = 1

    def get(self, request: Request, meeting_id):
        """
        List all meeting members.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        if not MeetingMember.objects\
                .filter(meeting=meeting, user=request.user, is_kicked=False)\
                .exists():
            return Response(status=403)

        # Get meeting member
        meeting_members = MeetingMember.objects.filter(meeting=meeting)

        # Validate data
        out_serializer = self.GetOutSerializer(meeting_members, many=True)

        # Return meeting
        return Response(out_serializer.data)
    
    class PostSerializer(MeetingMemberSerializer):
        class Meta(MeetingMemberSerializer.Meta):
            fields = ['user']

    class PostOutSerializer(MeetingMemberSerializer):
        class Meta(MeetingMemberSerializer.Meta):
            depth = 1
    
    def post(self, request: Request, meeting_id):
        """
        Create a new meeting member.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        if not GroupMember.objects\
                .filter(group=meeting.group, user=request.user, is_kicked=False)\
                .exists():
            return Response(status=403)
        
        # Get data from request
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save meeting
        meeting_member = serializer.save(meeting=meeting)

        # Validate data
        out_serializer = self.PostOutSerializer(meeting_member)

        # Return meeting
        return Response(out_serializer.data)
    

class MeetingMessageAPIView(APIView):

    """
    List all meeting messages, or create a new meeting message.
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(MeetingMessageSerializer):
        class Meta(MeetingMessageSerializer.Meta):
            depth = 1

    def get(self, request: Request, meeting_id):
        """
        List all meeting messages.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        if not MeetingMember.objects\
                .filter(meeting=meeting, user=request.user, is_kicked=False)\
                .exists():
            return Response(status=403)

        # Get meeting messages
        meeting_messages = MeetingMessage.objects.filter(meeting=meeting)

        # Validate data
        out_serializer = self.GetOutSerializer(meeting_messages, many=True)

        # Return meeting
        return Response(out_serializer.data)
    
    class PostSerializer(MeetingMessageSerializer):
        class Meta(MeetingMessageSerializer.Meta):
            fields = ['content']

    class PostOutSerializer(MeetingMessageSerializer):
        class Meta(MeetingMessageSerializer.Meta):
            depth = 1

    def post(self, request: Request, meeting_id):
        """
        Create a new meeting message.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        meeting_member = get_object_or_404(MeetingMember, meeting=meeting, user=request.user)

        # Get data from request
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save meeting
        meeting_message = serializer.save(meeting=meeting, sender=meeting_member.user)

        # Validate data
        out_serializer = self.PostOutSerializer(meeting_message)

        # Post event to websocket server
        try:
            requests.post(settings.WEBSOCKET_URL + f'on/meeting/{meeting.id}/message/')
        except Exception:
            pass

        # Return meeting
        return Response(out_serializer.data)


class MeetingMessageOneAPIView(APIView):

    """
    Get a meeting message, or update a meeting message.
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(MeetingMessageSerializer):
        class Meta(MeetingMessageSerializer.Meta):
            depth = 2

    def get(self, request: Request, meeting_id, message_id):
        """
        Get a meeting message.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        if not MeetingMember.objects\
                .filter(meeting=meeting, user=request.user, is_kicked=False)\
                .exists():
            return Response(status=403)

        # Get meeting message
        meeting_message = get_object_or_404(MeetingMessage, id=message_id, meeting=meeting)

        # Validate data
        out_serializer = MeetingMessageSerializer(meeting_message)

        # Return meeting
        return Response(out_serializer.data)
    
    class PatchSerializer(MeetingMessageSerializer):
        class Meta(MeetingMessageSerializer.Meta):
            fields = ['content']

    class PatchOutSerializer(MeetingMessageSerializer):
        class Meta(MeetingMessageSerializer.Meta):
            depth = 1

    def patch(self, request: Request, meeting_id, message_id):
        """
        Update a meeting message.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Get meeting message
        meeting_message = get_object_or_404(MeetingMessage, id=message_id, meeting=meeting)

        # Get data from request
        serializer = MeetingMessageSerializer(meeting_message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Save meeting
        meeting_message = serializer.save()

        # Validate data
        out_serializer = MeetingMessageSerializer(meeting_message)

        # Return meeting
        return Response(out_serializer.data)


class MeetingMessageAnnotationAPIView(APIView):

    """
    Get a meeting message annotation.
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(MeetingMessageAnnotationSerializer):
        class Meta(MeetingMessageAnnotationSerializer.Meta):
            depth = 1

    def get(self, request: Request, meeting_id, message_id):
        """
        Get a meeting message.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        if not MeetingMember.objects\
                .filter(meeting=meeting, user=request.user, is_kicked=False)\
                .exists():
            return Response(status=403)

        # Get meeting-message
        meeting_message = get_object_or_404(MeetingMessage, id=message_id, meeting=meeting)

        try:
            # Get meeting-message
            meeting_message_annotation = MeetingMessageAnnotation.objects.get(message=meeting_message)
            
            # Get meeting-messages
            out_serializer = self.GetOutSerializer(meeting_message_annotation)
        
        except MeetingMessageAnnotation.DoesNotExist:

            # Get meeting
            serializer = MeetingMessageSerializer(meeting_message)

            try:
                # Get meeting-messages
                response = requests.post(settings.ANNOTATOR_URL + f'ai/annotate/', json={
                    'description': meeting.description,
                    'content': serializer.data['content']
                })
                response.raise_for_status()

            except requests.exceptions.HTTPError as err:

                # Return meeting
                return Response(status=err.response.status_code)
            
            # Validate data
            serializer = MeetingMessageAnnotationSerializer(data=response.json())
            serializer.is_valid(raise_exception=True)

            # Save meeting
            meeting_message_annotation = serializer.save(message=meeting_message, meeting=meeting)

            # Validate data
            out_serializer = self.GetOutSerializer(meeting_message_annotation)

        # Return meeting
        return Response(out_serializer.data)
