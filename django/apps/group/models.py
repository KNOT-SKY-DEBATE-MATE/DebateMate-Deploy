import nh3
import uuid

from django.db import models
from django.contrib.auth import get_user_model


class Group(models.Model):

    """
    Group Model
    """

    # Group ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Group name
    name = models.CharField(max_length=255, unique=True)

    # Group description
    description = models.TextField(max_length=1024, blank=True)

    class Meta:

        # Model name
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def save(self, *args, **kwargs):
        """
        Sanitize group name and description
        """

        # Sanitize name
        self.name = nh3.clean_text(self.name)

        # Sanitize description
        self.description = nh3.clean_text(self.description)

        # Save
        super(Group, self).save(*args, **kwargs)


class GroupMember(models.Model):

    """
    Group Relationship Model
    """

    # Group
    group = models.ForeignKey(
        to='group.Group',
        on_delete=models.CASCADE, related_name='groupmember')

    # User
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE, related_name='groupmember')

    # Status of BAN
    is_kicked = models.BooleanField(default=False)

    # Status of ADMIN
    is_admin = models.BooleanField(default=False)

    class Meta:

        # Model name
        verbose_name = 'Group Relationship'
        verbose_name_plural = 'Group Relationships'

        # Unique constraint
        constraints = [
            # Unique constraint for group and user
            models.UniqueConstraint(
                fields=['group', 'user'], name='unique_group_user'),
        ]


class GroupMessage(models.Model):

    """
    Group Message Model
    """

    # Group
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    # Sender
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Content
    content = models.TextField(max_length=1024, blank=True)

    # Timestamp on which message was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Timestamp on which message was updated
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        # Model name
        verbose_name = 'Group Message'
        verbose_name_plural = 'Group Messages'

        # Ordering
        ordering = ['created_at']

    def save(self, *args, **kwargs):

        # Sanitize content
        self.content = nh3.clean_text(self.content)

        # Save
        super(GroupMessage, self).save(*args, **kwargs)
