from django.db import models
from guardian.shortcuts import get_perms, assign_perm
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

    def save(self, **kwargs):
        super().save(**kwargs)

        # fix attachment.view_attachment permission if needed
        if "attachment.view_attachment" not in get_perms(self.team.group, self):
            assign_perm("attachment.view_attachment", self.team.group, self)

        # fix attachment.add_attachment permission if needed
        if "attachment.add_attachment" not in get_perms(self.team.group, self):
            assign_perm("attachment.add_attachment", self.team.group)

        # fix attachment.change_attachment permission if needed
        if "attachment.change_attachment" not in get_perms(self.actor.user, self):
            assign_perm("attachment.change_attachment", self.actor.user, self)

        # fix attachment.delete_attachment permission if needed
        if "attachment.delete_attachment" not in get_perms(self.actor.user, self):
            assign_perm("attachment.delete_attachment", self.actor.user, self)
