from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy

from utils.models import UUIDBaseModel


def get_sentinel_user():
    """
    Function to get_or_create a "sentinel" User object, to carry the FK for Actor objects in cases where the original User object was deleted
    """
    return User.objects.get_or_create(username='deleted')[0]


class User(AbstractUser):
    """
    Our custom User model has no extra fields (for now)
    User objects can be deleted if the user so desires.
    """
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)


class Actor(UUIDBaseModel):
    """
    Everything in socialrating relates to an Actor rather than directly
    to a User object. An actor has a nullable OneToOneField to User.
    Actors are never deleted, but User objects can be deleted.
    """
    user = models.OneToOneField(
        'actor.User',
        on_delete=models.SET(get_sentinel_user),
    )

    def __str__(self):
        return "actor %s for user %s" % (self.uuid, self.user)

