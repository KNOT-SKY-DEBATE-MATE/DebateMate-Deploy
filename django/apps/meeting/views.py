# apps/meeting/views.py
import uuid

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.http.request import HttpRequest

from apps.group.models import (
    Group,
    GroupMember,
)

from .models import (
    Meeting,
)


class MeetingView(LoginRequiredMixin, View):

    """
    ミーティングを表示するページ。
    """

    def get(self, request: HttpRequest,  meeting_id: uuid.UUID):

        # ミーティングIDを取得
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # ユーザーがミーティングのメンバーかどうかを確認
        if not GroupMember.objects\
                .filter(group=meeting.group, user=request.user)\
                .exists():
            return HttpResponse(status=403)

        # グループをレンダリング
        return render(request, 'meeting.html', {
            'user': request.user,
            'meeting': meeting,
        })

class MeetingVideoView(LoginRequiredMixin, View):

    """
    ミーティングのビデオを表示するページ。
    """

    def get(self, request, meeting_id):
        
        # ミーティングを取得
        meeting = get_object_or_404(Meeting, id=meeting_id)

        # ミーティングIDを取得
        return render(request, 'meeting_userlist.html', {'meeting': meeting, 'user': request.user})