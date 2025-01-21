from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.http.request import HttpRequest



from .models import (
    Group,
    GroupMember,
)


class GroupView(LoginRequiredMixin, View):

    """
    View for group.
    """

    def get(self, request: HttpRequest, group_id):

        # Get group
        group = get_object_or_404(Group, id=group_id)

        # Check if user is a member of any group
        if not GroupMember.objects\
                .filter(group=group, user=request.user)\
                .exists():
            return HttpResponse(status=403)

        # Render group
        return render(request, 'group.html', {'group': group, 'user': request.user})
