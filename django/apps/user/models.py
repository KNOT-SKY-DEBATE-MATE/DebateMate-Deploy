import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractUser
)


class User(AbstractUser):

    # User UUID Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)