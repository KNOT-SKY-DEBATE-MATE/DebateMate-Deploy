from rest_framework import serializers

from .models import (
    Meeting,
    MeetingMember,
    MeetingMessage,
    MeetingMessageAnnotation
)


class MeetingSerializer(serializers.ModelSerializer):

    """
    Serializer for Meeting model.
    """

    class Meta:
        model = Meeting
        fields = '__all__'


class MeetingMemberSerializer(serializers.ModelSerializer):

    """
    Serializer for MeetingMember model.
    """

    class Meta:
        model = MeetingMember
        fields = '__all__'


class MeetingMessageSerializer(serializers.ModelSerializer):

    """
    Serializer for MeetingMessage model.
    """

    class Meta:
        model = MeetingMessage
        fields = '__all__'


class MeetingMessageAnnotationSerializer(serializers.ModelSerializer):

    """
    Serializer for MeetingMessageAnnotation model.
    """

    class Meta:
        model = MeetingMessageAnnotation
        fields = '__all__'
