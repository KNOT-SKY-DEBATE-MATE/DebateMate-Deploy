# apps/meeting/views.py
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.http.request import HttpRequest

from apps.group.models import (
    GroupMember,
)

from .models import (
    Meeting,
    MeetingMember,
)


class MeetingView(LoginRequiredMixin, View):

    """
    ミーティングを表示するページ。
    """

    def get(self, request: HttpRequest, meeting_id):

        # ミーティングIDを取得
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # ユーザーがミーティングのメンバーかどうかを確認
        try:
            GroupMember.objects.get(user=request.user, group=meeting.group)
        except GroupMember.DoesNotExist:
            return HttpResponse(status=403)
        
        # Create or get meeting-member
        MeetingMember.objects.get_or_create(user=request.user, meeting=meeting)

        # グループをレンダリング
        return render(request, 'meeting.html', {
            'user': request.user,
            'meeting': meeting,
        })

class MeetingVideoView(LoginRequiredMixin, View):

    """
    ミーティングのビデオを表示するページ。
    """

    def get(self, request: HttpRequest, meeting_id):
        
        # ミーティングを取得
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # ユーザーがミーティングのメンバーかどうかを確認
        try:
            GroupMember.objects.get(user=request.user, group=meeting.group)
        except GroupMember.DoesNotExist:
            return HttpResponse(status=403)
        
        # Create or get meeting-member
        MeetingMember.objects.get_or_create(user=request.user, meeting=meeting)

        # ミーティングIDを取得
        return render(request, 'meeting_userlist.html', {
            'user': request.user,
            'meeting': meeting,
        })