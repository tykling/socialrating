import uuid
import logging

from django.db import models
from django.contrib.auth.models import AbstractUser

logger = logging.getLogger("socialrating.%s" % __name__)


def get_sentinel_user():
    """
    Function to get_or_create a "sentinel" User object, to carry the FK for Actor objects in cases where the original User object was deleted
    """
    return User.objects.get_or_create(username="deleted")[0]


class User(AbstractUser):
    """
    Our custom User model has no extra fields (for now)
    User objects can be deleted if the user so desires.
    """

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def actor(self):
        """
        Create or return the Actor object for this user
        """
        return Actor.objects.get_or_create(user=self)[0]

    def save(self, **kwargs):
        if self._state.adding:
            create_actor = True
        else:
            create_actor = False
        super().save(**kwargs)
        if create_actor:
            # just accessing the actor property creates the Actor..
            _ = self.actor


class Actor(models.Model):
    """
    Everything in socialrating relates to an Actor rather than directly
    to a User object. An actor has FK to User. Actors are never deleted,
    but User objects can be deleted.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "actor.User",
        on_delete=models.SET(get_sentinel_user),
        help_text="The Django User object this Actor belongs to (might be 'deleted' if the User was deleted)",
    )

    def __str__(self):
        return "actor %s for user %s" % (self.uuid, self.user)
