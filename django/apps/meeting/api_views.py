# apps/meeting/api_views.py
import requests
import logging
import math

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
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


# Get logger
LOGGER = logging.getLogger(__name__)


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

        # Authorize user as meeting-member
        try:
            GroupMember.objects.get(user=request.user, group=serializer.validated_data['group'], is_kicked=False)
        except GroupMember.DoesNotExist:
            return Response(status=403)
        
        # Save meeting
        meeting: Meeting = serializer.save()

        # Save meeting-member
        MeetingMember.objects.create(user=request.user, meeting=meeting)

        # Send event to websocket
        try:
            response = requests.post(settings.WEBSOCKET_URL + f'on/group/{meeting.group.id}/meeting.create')
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            LOGGER.error(f"HTTP error occurred: {e}")
            return Response(status=e.response.status_code)
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"An error occurred: {e}")
            return Response(status=e.response.status_code)    
        
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
        Redirect
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Authorize user as group-member
        try:
            MeetingMember.objects.get(user=request.user, meeting=meeting)
        except MeetingMember.DoesNotExist:
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

        # Authorize user as group-member
        try:
            MeetingMember.objects.get(user=request.user, meeting=meeting)
        except MeetingMember.DoesNotExist:
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

        # Authorize user as group-member
        try:
            MeetingMember.objects.get(meeting=meeting, user=request.user, is_kicked=False)
        except MeetingMember.DoesNotExist:
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

        # Authorize user as group-member
        try:
            MeetingMember.objects.get(user=request.user, meeting=meeting)
        except GroupMember.DoesNotExist:
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
    

class MeetingMemberKickAPIView(APIView):
    """
    Meeting Member Kick
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, meeting_id):
        """
        Get current kick votes
        """
        meeting = get_object_or_404(Meeting, id=meeting_id)
        
        # キャッシュからデータを取得
        votebox_key = f'meeting.kick.votes:{meeting.id}'
        votebox = cache.get(votebox_key, {})
        
        # フロントエンド用にデータを整形
        kick_status = []
        for member_id, vote_data in votebox.items():
            kick_status.append({
                'member_id': member_id,
                'votes': len(vote_data['voters']),
                'is_kicked': vote_data['is_kicked']
            })
        
        return Response(kick_status)

    def post(self, request: Request, meeting_id):
        """
        Create or update kick vote
        """
        # Get meeting object
        meeting = get_object_or_404(Meeting, id=meeting_id)
        
        # Authorize user as group-member
        try:
            meeting_member = MeetingMember.objects.get(user=request.user, meeting=meeting)
        except MeetingMember.DoesNotExist:
            return Response(status=403)
        
        # リクエストからターゲットメンバーIDを取得
        target_member_id = request.data.get('member_id')
        if not target_member_id:
            return Response({'error': 'member_id is required'}, status=400)

        # Key of cache
        votebox_key = f'meeting.kick.votes:{meeting.id}'
        
        # Cache get by key
        votebox = cache.get(votebox_key, {})
        
        # 投票データの構造を初期化
        if target_member_id not in votebox:
            votebox[target_member_id] = {
                'voters': [],
                'is_kicked': False
            }
        
        # 投票者を追加
        voter_id = str(request.user.id)
        if voter_id not in votebox[target_member_id]['voters']:
            votebox[target_member_id]['voters'].append(voter_id)

        # 必要な投票数を計算（過半数）
        member_count = MeetingMember.objects.filter(meeting=meeting).count()
        required_votes = math.ceil(member_count / 2)

        # キック状態の更新
        current_votes = len(votebox[target_member_id]['voters'])
        votebox[target_member_id]['is_kicked'] = current_votes >= required_votes

        # Set votes with timeout (3 minutes)
        cache.set(votebox_key, votebox, timeout=180)  # 3*60 seconds

        # Return response
        return Response({
            'success': True,
            'current_votes': current_votes,
            'required_votes': required_votes,
            'is_kicked': votebox[target_member_id]['is_kicked']
        })

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
        try:
            MeetingMember.objects.get(meeting=meeting, user=request.user, is_kicked=False)
        except MeetingMember.DoesNotExist:
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
        try:
            MeetingMember.objects.get(meeting=meeting, user=request.user, is_kicked=False)
        except MeetingMember.DoesNotExist:
            return Response(status=403)

        # Get data from request
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save meeting
        meeting_message = serializer.save(meeting=meeting, sender=request.user)

        # Validate data
        out_serializer = self.PostOutSerializer(meeting_message)

        # Post event to websocket server
        try:
            response = requests.post(settings.WEBSOCKET_URL + f'on/meeting/{meeting.id}/message.create/')
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            LOGGER.error(f"HTTP error occurred: {e}")
            return Response(status=e.response.status_code)
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"An error occurred: {e}")
            return Response(status=e.response.status_code)    

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
        try:
            MeetingMember.objects.get(meeting=meeting, user=request.user, is_kicked=False)
        except MeetingMember.DoesNotExist:
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


class MeetingMessageAnnotationAPIView(APIView):
    """
    Get a meeting message annotation.
    """

    permission_classes = [IsAuthenticated]

    class GetOutSerializer(MeetingMessageAnnotationSerializer):
        class Meta(MeetingMessageAnnotationSerializer.Meta):
            depth = 1

    class ExternalPostSerializer(MeetingMessageAnnotationSerializer):
        class Meta(MeetingMessageAnnotationSerializer.Meta):
            fields = ['summary', 'suggestion', 'criticism', 'evaluation', 'warning', 'is_policy_violation']

    def get(self, request: Request, meeting_id, message_id):
        """
        Get a meeting message.
        """

        # Get meeting
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # Check if user is a member of any meeting
        try:
            MeetingMember.objects.get(meeting=meeting, user=request.user, is_kicked=False)
        except MeetingMember.DoesNotExist:
            return Response(status=403)

        # Get meeting-message
        meeting_message = get_object_or_404(MeetingMessage, id=message_id)

        try:
            # Get meeting-message
            meeting_message_annotation = MeetingMessageAnnotation.objects.get(message=meeting_message)
            
            # Get meeting-messages
            out_serializer = self.GetOutSerializer(meeting_message_annotation)
        
        except MeetingMessageAnnotation.DoesNotExist:

            # Get meeting
            serializer = MeetingMessageSerializer(meeting_message)
            
            # Get annotation
            try:
                response = requests.post(settings.ANNOTATOR_URL + 'ai/annotate/', json={
                    'description': meeting.description,
                    'content': serializer.data['content']
                })
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                LOGGER.error(f"HTTP error occurred: {e}")
                return Response(status=e.response.status_code)
            except requests.exceptions.RequestException as e:
                LOGGER.error(f"An error occurred: {e}")
                return Response(status=e.response.status_code)
            
            # Validate data
            serializer = self.ExternalPostSerializer(data=response.json())
            serializer.is_valid(raise_exception=True)

            # Save meeting
            meeting_message_annotation = serializer.save(message=meeting_message)

            # Validate data
            out_serializer = self.GetOutSerializer(meeting_message_annotation)

        # Return meeting
        return Response(out_serializer.data)
    
    def post(self, request: Request, meeting_id, message_id):
        # Get meeting-message
        meeting_message = get_object_or_404(MeetingMessage, id=message_id)

        # Get data from request
        serializer = self.ExternalPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ポリシー違反を検出した場合
        if serializer.validated_data['is_policy_violation']:
            # 該当するミーティングメンバーを取得
            member = MeetingMember.objects.get(meeting__id=meeting_id, user=meeting_message.sender)
            
            # 自動でキックする
            member.is_kicked = True
            member.save()

            # キック投票を行う
            self.create_kick_vote(meeting_id, member.id)

        # 既存の処理は省略

    def create_kick_vote(self, meeting_id, member_id):
        # キャッシュキーを作成
        votebox_key = f'meeting.kick.votes:{meeting_id}'
        
        # キャッシュからデータを取得
        votebox = cache.get(votebox_key, {})
        
        # 投票データを初期化
        if member_id not in votebox:
            votebox[member_id] = {
                'voters': [],
                'is_kicked': False
            }
        
        # 投票者を追加
        votebox[member_id]['voters'].append(str(self.request.user.id))

        # 必要な投票数を計算（過半数）
        member_count = MeetingMember.objects.filter(meeting__id=meeting_id).count()
        required_votes = math.ceil(member_count / 2)

        # キック状態の更新
        current_votes = len(votebox[member_id]['voters'])
        votebox[member_id]['is_kicked'] = current_votes >= required_votes

        # キャッシュに保存
        cache.set(votebox_key, votebox, timeout=180)