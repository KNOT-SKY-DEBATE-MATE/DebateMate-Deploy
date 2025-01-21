import nh3
import uuid

from django.db import models
from django.contrib.auth import get_user_model
from apps.group.models import (
    Group,
)


class Meeting(models.Model):

    """
    Discussion Model
    """

    # Unique ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Fields
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE)

    # Fields
    title = models.CharField(max_length=255)

    # Fields
    description = models.TextField(max_length=1024, blank=True)

    # Fields
    is_archived = models.BooleanField(default=False)

    class Meta:

        # Model options
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'

        # Constraints
        constraints = [
            # Unique constraint for group and title
            models.UniqueConstraint(
                fields=['group', 'title'], name='unique_group_title'),
        ]

    def save(self, *args, **kwargs):
        """
        Save meeting
        """

        # Sanitize title
        self.title = nh3.clean_text(self.title)

        # Sanitize description
        self.description = nh3.clean_text(self.description)

        # Save
        super(Meeting, self).save(*args, **kwargs)


class MeetingMember(models.Model):

    """
    Discussion Member Model
    """

    # Fields
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    # Fields
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Fields
    is_kicked = models.BooleanField(default=False)

    class Meta:

        # Model options
        verbose_name = 'Meeting Member'
        verbose_name_plural = 'Meeting Members'

        # Constraints
        constraints = [
            # Unique constraint for meeting and member
            models.UniqueConstraint(
                fields=['meeting', 'user'], name='unique_meeting_member'),
        ]

    

class MeetingMessage(models.Model):

    """
    Discussion Message Model
    """

    # Unique ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Fields
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    # Fields
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Fields
    content = models.TextField(max_length=1024, blank=True)

    # Fields
    created_at = models.DateTimeField(auto_now_add=True)

    # Fields
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        # Model options
        verbose_name = 'Meeting Message'
        verbose_name_plural = 'Meeting Messages'

        # Ordering
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        """
        Save message
        """

        # Sanitize content
        self.content = nh3.clean_text(self.content)

        # Save
        super(MeetingMessage, self).save(*args, **kwargs)


class MeetingMessageAnnotation(models.Model):

    """
    Discussion Message Summary Model
    """

    # Fields
    message = models.ForeignKey(MeetingMessage, on_delete=models.CASCADE)

    # Fields
    summary = models.TextField(max_length=255, blank=True)

    # Fields
    suggestion = models.TextField(max_length=255, blank=True)

    # Fields
    criticism = models.TextField(max_length=255, blank=True)

    # Fields
    evaluation = models.TextField(max_length=255, blank=True)

    # Fields
    warning = models.TextField(max_length=255, blank=True)

    # Fields
    is_policy_violation = models.BooleanField(default=False)

    class Meta:

        # Model options
        verbose_name = 'Meeting Message Annotation'
        verbose_name_plural = 'Meeting Message Annotations'

    def save(self, *args, **kwargs):
        """
        Save message
        """

        # Sanitize summary
        self.summary = nh3.clean_text(self.summary)

        # Sanitize suggestions
        self.suggestion = nh3.clean_text(self.suggestion)

        # Sanitize criticism
        self.criticism = nh3.clean_text(self.criticism)

        # Sanitize evaluation
        self.evaluation = nh3.clean_text(self.evaluation)

        # Sanitize warning
        self.warning = nh3.clean_text(self.warning)

        # Save
        super(MeetingMessageAnnotation, self).save(*args, **kwargs)
