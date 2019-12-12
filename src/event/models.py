import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Event(models.Model):
    """
    The Event model consists of:
    - an event type
    - an Actor FK to the Actor who triggered the event
    - a GenericForeignKey to the object the event relates to
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="events",
        help_text="The Django content_type of the model for the object this Event relates to.",
    )

    object_id = models.CharField(
        max_length=36, help_text="The PK/UUID of the object this Event relates to."
    )

    event_object = GenericForeignKey("content_type", "object_id")

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

    EVENT_TYPES = ((CREATE, "Create"), (UPDATE, "Update"), (DELETE, "Delete"))

    event_type = models.CharField(
        max_length=6, choices=EVENT_TYPES, help_text="The type of event"
    )

    actor = models.ForeignKey(
        "actor.Actor",
        on_delete=models.PROTECT,
        help_text="The Actor who caused this event.",
    )

    timestamp = models.DateTimeField(
        default=timezone.now, help_text="The date and time when this Event happened."
    )
