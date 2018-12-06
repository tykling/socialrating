import uuid, logging

from django.db import models
from django.core.exceptions import ValidationError
from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation

from eventlog.models import Event

logger = logging.getLogger("socialrating.%s" % __name__)


class BaseModel(models.Model):
    """
    All models in this project are subclassed from this BaseModel
    """
    class Meta:
        abstract = True

    created = models.DateTimeField(
        auto_now_add=True,
        help_text='The date and time when this object was created.'
    )

    updated = models.DateTimeField(
        auto_now=True,
        help_text='The date and time when this object was last updated.'
    )

    events = GenericRelation(Event)

    def save(self, **kwargs):
        """
        call the models full_clean() method before saving,
        which in turn calls .clean_fields(), .clean() and 
        .validate_unique()
        """
        try:
            self.full_clean()
        except ValidationError as e:
            message = "Got ValidationError while saving: %s" % e
            if hasattr(self, 'request'):
                messages.error(self.request, message)
            logger.error(message)
            # dont save, re-raise the exception
            raise
        super().save(**kwargs)


class UUIDBaseModel(BaseModel):
    """
    A BaseModel to make models use an uuid as PK
    """
    class Meta:
        abstract = True

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

