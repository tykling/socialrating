from django.db import models
from guardian.shortcuts import assign_perm
from django.shortcuts import reverse

from utils.models import UUIDBaseModel
from utils.uploads import get_attachment_path


class Attachment(UUIDBaseModel):
    """
    An Attachment is any file uploaded in the system.
    All attachments belong to a Review.
    """

    class Meta:
        ordering = ["pk"]

    review = models.ForeignKey(
        "review.Review",
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text="The Review to which this Attachment belongs.",
    )

    attachment = models.FileField(help_text="The file", upload_to=get_attachment_path)

    mimetype = models.CharField(
        max_length=255,
        help_text="The mimetype of this file as detected by python-magic on upload.",
    )

    size = models.IntegerField(help_text="The size in bytes of this file")

    description = models.CharField(
        max_length=255, help_text="The description for this attachment.", blank=True
    )

    filterfield = "review"
    filtervalue = "review"
    breadcrumb_list_name = "Attachments"

    def get_absolute_url(self):
        return reverse(
            "team:category:item:review:attachment:detail",
            kwargs={
                "team_slug": self.item.category.team.slug,
                "category_slug": self.item.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.review.uuid,
                "attachment_uuid": self.uuid,
            },
        )

    @property
    def team(self):
        return self.review.item.category.team

    @property
    def category(self):
        return self.review.item.category

    @property
    def item(self):
        return self.review.item

    @property
    def actor(self):
        return self.review.actor

    def grant_permissions(self):
        """
        - All team members may view an Attachment
        - The Review author may change the Attachment
        - The Review author may delete the Attachment
        """
        assign_perm("attachment.view_attachment", self.team.group, self)
        assign_perm("attachment.change_attachment", self.review.actor.user, self)
        assign_perm("attachment.delete_attachment", self.review.actor.user, self)

    def save(self, **kwargs):
        """
        Save Attachment and grant permissions
        """
        super().save(**kwargs)
        self.grant_permissions()
