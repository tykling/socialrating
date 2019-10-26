import uuid
import logging

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib import messages

from eventlog.models import Event

logger = logging.getLogger("socialrating.%s" % __name__)


class BaseModel(models.Model):
    """
    All models in this project are subclassed from this BaseModel
    It adds created and updated datetime fields. It also sets it so
    no default permissions are created for new model instances.
    """

    class Meta:
        abstract = True
        default_permissions = ()

    created = models.DateTimeField(
        help_text="The date and time when this object was created."
    )

    updated = models.DateTimeField(
        help_text="The date and time when this object was last updated."
    )

    events = GenericRelation(Event)

    def save(self, **kwargs):
        """
        Always validate before saving, even if the save doesn't
        happen inside a form:
        Call the models full_clean() method before saving,
        which in turn calls .clean_fields(), .clean() and
        .validate_unique()
        """
        # create a slug if we don't already have one. Max 50 chars.
        if hasattr(self, "slug") and not self.slug:
            self.slug = slugify(self.name[0:50])
            if not self.slug:
                raise Exception("Unable to slugify, cannot save")

        # update the timestamps before saving
        if not self.created:
            self.created = timezone.now()
        self.updated = timezone.now()

        # do the validation
        try:
            self.full_clean()
        except ValidationError as e:
            message = "Got ValidationError while saving %s %s: %s" % (
                self.__class__,
                self,
                e,
            )
            if hasattr(self, "request"):
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

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
