from django.db import models

from utils.models import UUIDBaseModel


class Comment(UUIDBaseModel):
    """
    A Review is linked to an Actor and an Item.
    All Ratings are linked to a Review.
    """

    class Meta:
        ordering = ["-created"]
        permissions = (
            ("add_attachment", "Add Attachment to this Review"),
            ("add_vote", "Add Vote for this Review"),
        )

    actor = models.ForeignKey(
        "actor.Actor",
        on_delete=models.PROTECT,
        related_name="reviews",
        help_text="The Actor who made this Review",
    )
