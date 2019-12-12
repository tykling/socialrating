from django.db import models
from guardian.shortcuts import assign_perm
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse_lazy


from utils.models import UUIDBaseModel
from utils.uploads import get_attachment_path


class Attachment(UUIDBaseModel):
    """
    An Attachment is any file uploaded in the system.
    All attachments belong to a Review.
    """

    actor = models.ForeignKey(
        "actor.Actor",
        on_delete=models.PROTECT,
        related_name="attachments",
        help_text="The Actor who uploaded this Attachment blabla.",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="attachments",
        help_text="The Django content_type of the model for the object this Event relates to.",
    )

    object_id = models.CharField(
        max_length=36, help_text="The PK/UUID of the object this Event relates to."
    )

    attachment_object = GenericForeignKey("content_type", "object_id")

    attachment = models.FileField(help_text="The file", upload_to=get_attachment_path)

    mimetype = models.CharField(
        max_length=255,
        help_text="The mimetype of this file as detected by python-magic on upload.",
    )

    size = models.IntegerField(help_text="The size in bytes of this file")

    description = models.CharField(
        max_length=255, help_text="The description for this attachment.", blank=True
    )

    breadcrumb_list_name = "Attachments"

    @property
    def breadcrumb_detail_name(self):
        return self.description[0:50] or self.uuid

    @property
    def detail_url_kwargs(self):
        kwargs = self.attachment_object.detail_url_kwargs
        kwargs["attachment_uuid"] = self.uuid
        return kwargs

    def get_url(self, action):
        """
        This method resolves the requested action of the Attachment object
        """
        kwargs = self.attachment_object.detail_url_kwargs
        url = f"{self.attachment_object.object_url_namespace}:attachment"
        if action != "list":
            kwargs.update({"attachment_uuid": self.uuid})
        url += f":{action}"
        return reverse_lazy(url, kwargs=kwargs)

    def get_list_url(self):
        return self.get_url("list")

    def get_absolute_url(self):
        return self.get_url("detail")

    def get_settings_url(self):
        return self.get_url("settings")

    def get_update_url(self):
        return self.get_url("update")

    def get_delete_url(self):
        return self.get_url("delete")

    def get_file_url(self):
        return self.get_url("file")

    @property
    def team(self):
        return self.attachment_object.team

    def grant_permissions(self):
        """
        - All team members may view an Attachment
        - The Attachment uploader may change the Attachment
        - The Attachment uploader or a team admin may delete the Attachment
        """
        assign_perm("attachment.view_attachment", self.team.group, self)
        assign_perm("attachment.change_attachment", self.actor.user, self)
        assign_perm("attachment.delete_attachment", self.actor.user, self)
        assign_perm("attachment.delete_attachment", self.team.admingroup, self)

    def save(self, **kwargs):
        """
        Save Attachment and grant permissions
        """
        super().save(**kwargs)
        self.grant_permissions()
