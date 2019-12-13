import uuid
import logging
import threading

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from crum import get_current_user
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from event.models import Event

logger = logging.getLogger("socialrating.%s" % __name__)
request_local = threading.local()


class CleanedModel(models.Model):
    """
    Always validate before saving, even if the save doesn't
    happen inside a form. So we call the models full_clean()
    method before saving, which in turn calls .clean_fields(),
    .clean() and .validate_unique().
    """

    class Meta:
        abstract = True

    def save(self, **kwargs):
        # do the validation
        try:
            self.full_clean()
        except ValidationError as e:
            message = "Got ValidationError while saving %s %s: %s" % (
                self.__class__,
                self,
                e,
            )
            if hasattr(self, "request") and self.request:
                messages.error(self.request, message)
            logger.error(message)
            # dont save, re-raise the exception
            raise
        super().save(**kwargs)


class SlugModel(CleanedModel):
    """ Create a slug if we don't already have one. Max 50 chars. """

    class Meta(CleanedModel.Meta):
        abstract = True

    # override this if the model uses a different field for the slug "source"
    slug_field = "name"

    def get_slug(self, prefix=""):
        """
        Shared slugify method which ensures we get a slug or raise an exception
        """
        # do we have a value to slugify?
        if not hasattr(self, self.slug_field) or not getattr(self, self.slug_field):
            raise ValidationError(
                "No attribute self.slug_field found on this model, or attribute is empty"
            )

        # get slug
        slug = slugify((prefix + getattr(self, self.slug_field)))[0:50]
        if not slug:
            # hello David :)
            raise ValidationError("Unable to slugify, cannot save")

        # return the result
        return slug

    def save(self, **kwargs):
        """
        If a model has an empty slug field at this point we fall back to this
        default slugify code which can be overridden in models as needed.
        """
        if hasattr(self, "slug") and not self.slug:
            self.slug = self.get_slug()
        super().save(**kwargs)


class TimestampedModel(SlugModel):
    """ Adds created and updated fields, and override save() to update timestamps """

    class Meta(SlugModel.Meta):
        abstract = True

    created = models.DateTimeField(
        default=timezone.now,
        help_text="The date and time when this object was created.",
    )

    updated = models.DateTimeField(
        default=timezone.now,
        help_text="The date and time when this object was last updated.",
    )

    def save(self, **kwargs):
        if not self.created:
            self.created = timezone.now()
        self.updated = timezone.now()
        # call SlugModel.save()
        super().save(**kwargs)


class GFKModel(TimestampedModel):
    """
    Adds GenericRelation for comments and attachments, and an
    events property which does sorta the same as a GenericRelation.
    """

    class Meta(TimestampedModel.Meta):
        abstract = True

    comments = GenericRelation("comment.Comment", help_text="Comments for this object")

    attachments = GenericRelation(
        "attachment.Attachment", help_text="Attachments for this object"
    )

    @property
    def events(self):
        """
        Return all Events which relate directly to this object.
        We can't use a GenericRelation here because then the Events
        would be deleted when the object does.
        """
        from event.models import Event

        return Event.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.uuid
        )

    def get_comment_count(self, obj=None):
        """
        Return the number of comments on the object (recursively)
        """
        if not obj:
            obj = self
        count = obj.comments.count()
        if count:
            for comment in obj.comments.all():
                count += self.get_comment_count(comment)
        return count

    def get_comment_attachment_count(self, obj=None):
        """
        Return the number of attachments on comments on the object (recursively)
        """
        if not obj:
            obj = self
        count = obj.attachments.count()
        if obj.comments.exists():
            for comment in obj.comments.all():
                count += self.get_attachment_count(comment)
        return count


class EventModel(GFKModel):
    """
    Create an Event object before saving or deleting
    """

    class Meta(GFKModel.Meta):
        abstract = True

    @property
    def request(self):
        return getattr(request_local, "request", None)

    def save(self, **kwargs):
        """
        We override save() to add an Event before creating or updating the object.
        """
        # get request from TLS if possible
        user = get_current_user()
        if user:
            actor = user.actor
        else:
            from actor.models import User

            actor = User.get_anonymous().actor

        # add event
        Event.objects.create(
            event_type=Event.CREATE if self._state.adding else Event.UPDATE,
            actor=actor,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.uuid,
        )
        # call GFKModel.save()
        super().save(**kwargs)

    def delete(self, **kwargs):
        """
        We override delete() to add an Event before deleting the object.
        """
        # get user
        user = get_current_user()
        if user:
            actor = user.actor
        else:
            from actor.models import User

            actor = User.get_anonymous().actor

        # add event
        Event.objects.create(
            event_type=Event.CREATE if self._state.adding else Event.UPDATE,
            actor=actor,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.uuid,
        )
        super().delete(**kwargs)


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class TaggedModel(EventModel):
    """
    Add taggit to models
    """

    class Meta(GFKModel.Meta):
        abstract = True

    tags = TaggableManager(through=UUIDTaggedItem, blank=True)


class UUIDBaseModel(TaggedModel):
    """
    All models in this project are subclassed from this BaseModel.
    It just sets a few default Meta options and sets an uuidfield as pk.
    """

    class Meta(TaggedModel.Meta):
        abstract = True
        ordering = ["-created"]
        get_latest_by = "created"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    @property
    def detail_url_kwargs(self):
        """
        We fill this dict with kwargs in the models so GFK objects can always find their way home
        """
        return {}

    """
    we set this to the relevant namespace in each model so the GFK objects can build nice urls,
    for example in review.models.Review this would be set to "team:category:item:review"
    """
    object_url_namespace = ""

    """
    A default breadcrumb text for listviews, override as needed
    """
    breadcrumb_list_name = "objects"

    @property
    def object_name(self):
        return self._meta.object_name

    @property
    def breadcrumb_detail_name(self):
        """
        A default breadcrumb text for detailviews.
        Override in models as needed.
        """
        return self.name
