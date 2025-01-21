import uuid
import nh3

from django.db import models
from django.contrib.auth.models import (
    AbstractUser
)


class User(AbstractUser):

    # User UUID Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def save(self):
        self.first_name = nh3.clean_text(self.first_name)
        self.last_name = nh3.clean_text(self.last_name)
        self.username = nh3.clean_text(self.username)