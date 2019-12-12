from django.db import models
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from guardian.shortcuts import assign_perm

from utils.models import UUIDBaseModel


class Comment(UUIDBaseModel):
    """
    The Comment model contains all comments. A Comment either has a reply_to, or it
    has a GFK to the object the Comment is about (like an Item or Attachment or forum Thread)
    """

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="comments",
        help_text="The Django content_type of the model for the object this Comment relates to.",
    )

    object_id = models.CharField(
        max_length=36, help_text="The PK/UUID of the object this Comment relates to."
    )

    comment_object = GenericForeignKey("content_type", "object_id")

    reply_to = models.ForeignKey(
        "comment.Comment",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
        help_text="The Comment this Comment is a reply to, if any",
    )

    actor = models.ForeignKey(
        "actor.Actor",
        on_delete=models.PROTECT,
        related_name="comments",
        help_text="The Actor who made this Comment.",
    )

    subject = models.CharField(max_length=100, help_text="The subject of this Comment.")

    body = models.TextField(
        help_text="The body of this Comment. Markdown is supported."
    )

    breadcrumb_list_name = "Comments"

    def clean(self):
        if self.reply_to and self.comment_object != self.reply_to.comment_object:
            raise ValidationError("Cannot add a reply for a different comment_object")

    @property
    def object_url_namespace(self):
        return self.comment_object.object_url_namespace + ":comment"

    @property
    def detail_url_kwargs(self):
        kwargs = self.comment_object.detail_url_kwargs
        kwargs["comment_uuid"] = self.uuid
        return kwargs

    @property
    def breadcrumb_detail_name(self):
        return self.subject[0:50]

    def grant_permissions(self):
        """
        - All team members may view a Comment
        - Author may update a Comment
        - Admins and author may delete a Comment
        - All team members may create new Comments as replies to this comment
        """
        assign_perm("comment.view_comment", self.team.group, self)
        assign_perm("comment.change_comment", self.actor.user, self)
        assign_perm("comment.delete_comment", self.team.admingroup, self)
        assign_perm("comment.delete_comment", self.actor.user, self)
        assign_perm("comment.add_comment", self.team.group, self)

    def save(self, **kwargs):
        """
        Save the Comment and grant permissions.
        """
        super().save(**kwargs)
        self.grant_permissions()

    @property
    def team(self):
        return self.comment_object.team

    def get_url(self, urlname):
        """
        This method resolves the requested urlname of the Comment object
        """
        kwargs = self.comment_object.detail_url_kwargs
        kwargs.update({"comment_uuid": self.uuid})
        return reverse_lazy(
            self.comment_object.object_url_namespace + ":comment:" + urlname,
            kwargs=kwargs,
        )

    def get_absolute_url(self):
        return self.get_url("detail")

    def get_settings_url(self):
        return self.get_url("settings")

    def get_update_url(self):
        return self.get_url("update")

    def get_delete_url(self):
        return self.get_url("delete")
