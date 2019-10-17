from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from guardian.shortcuts import get_perms, assign_perm

from team.models import TeamRelatedModel, TeamRelatedUUIDModel


class Review(TeamRelatedUUIDModel):
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

    item = models.ForeignKey(
        "item.Item",
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="The Item this Review applies to",
    )

    context = models.ForeignKey(
        "context.Context",
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="The Context to which this Review belongs.",
    )

    headline = models.CharField(
        max_length=100, help_text="A short headline for this review"
    )

    body = models.TextField(
        help_text="The text review. Optional. Markdown is supported (or will be at some point).",
        null=True,
        blank=True,
    )

    team_filter = "item__category__team"
    breadcrumb_list_name = "Reviews"

    @property
    def team(self):
        return self.item.category.team

    @property
    def category(self):
        return self.item.category

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        return reverse_lazy(
            "team:category:item:review:detail",
            kwargs={
                "team_slug": self.item.category.team.slug,
                "category_slug": self.item.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.pk,
            },
        )

    def grant_permissions(self):
        """
        - All team members may see a review
        - Only the Review author may change the Review
        - Only team admins and the Review author may delete a Review
        """
        assign_perm("review.view_review", self.team.group, self)
        assign_perm("review.change_review", self.actor.user, self)
        assign_perm("review.delete_review", self.actor.user, self)
        assign_perm("review.delete_review", self.team.admingroup, self)
        assign_perm("review.add_attachment", self.actor.user, self)
        assign_perm("review.add_vote", self.actor.user, self)

    def save(self, **kwargs):
        super().save(**kwargs)
        self.grant_permissions()

    def ratings_missing_votes(self):
        return self.category.ratings.all().exclude(
            id__in=self.votes.all().values_list("rating_id", flat=True)
        )
