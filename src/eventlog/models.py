import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Event(models.Model):
    """
    The Event model consists of:
    - an event type FK
    - a GenericForeignKey to the object the event relates to
    - an Actor FK to the Actor who triggered the event
    """
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

    EVENT_TYPES = (
        (CREATE, 'Create'),
        (UPDATE, 'Update'),
        (DELETE, 'Delete'),
    )

    event_type = models.CharField(
        max_length=6,
        choices=EVENT_TYPES,
        help_text='The type of event.'
    )

    actor = models.ForeignKey(
        'actor.Actor',
        on_delete=models.PROTECT,
        help_text='The Actor who caused this event.'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='events',
        help_text='The Django content_type of the model for the object this Event relates to.',
    )

    object_id = models.CharField(
        max_length=32,
        help_text='The PK/UUID of the object this Event relates to.',
    )

    # the GenericForeignKey ties this Event to the object
    event_object = GenericForeignKey(
        'content_type',
        'object_id',
    )

