from rest_framework import serializers

from .models import (
    Group,
    GroupMember,
    GroupMessage,
)


class GroupSerializer(serializers.ModelSerializer):

    """
    Serializer for Group model.
    """

    class Meta:
        model = Group
        fields = '__all__'


class GroupMemberSerializer(serializers.ModelSerializer):

    """
    Serializer for GroupMember model.
    """

    class Meta:
        model = GroupMember
        fields = '__all__'


class GroupMessageSerializer(serializers.ModelSerializer):

    """
    Serializer for GroupMessage model.
    """

    class Meta:
        model = GroupMessage
        fields = '__all__'
