from django.db import models
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from guardian.shortcuts import assign_perm

from utils.models import UUIDBaseModel


class Vote(UUIDBaseModel):
    """
    A Vote contains a reference to a Rating and a Review,
    as well as the actual Vote (a PositiveIntegerField).
    It may also optionally contain a short comment related to this specific vote.
    """

    class Meta(UUIDBaseModel.Meta):
        unique_together = [("review", "rating")]

    review = models.ForeignKey(
        "review.Review",
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="The Review this Vote belongs to.",
    )

    rating = models.ForeignKey(
        "rating.Rating",
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="The Rating this Vote applies to.",
    )

    vote = models.PositiveIntegerField(
        help_text="The actual numerical vote for this Rating."
    )

    comment = models.CharField(
        max_length=1000,
        help_text="An optional short comment related to this specific vote. 1000 character limit.",
        blank=True,
        null=True,
    )

    filterfield = "review"
    filtervalue = "review"
    breadcrumb_list_name = "Votes"

    @property
    def breadcrumb_detail_name(self):
        return self.rating.name

    @property
    def team(self):
        return self.review.item.category.team

    @property
    def category(self):
        return self.review.item.category

    @property
    def item(self):
        return self.review.item

    def grant_permissions(self):
        """
        - All team members may see a vote
        - Only the Review author may change the Vote
        - Only team admins and the Review author may delete a Vote
        """
        assign_perm("vote.view_vote", self.team.group, self)
        assign_perm("vote.change_vote", self.review.actor.user, self)
        assign_perm("vote.delete_vote", self.review.actor.user, self)
        assign_perm("vote.delete_vote", self.team.admingroup, self)

    def save(self, **kwargs):
        """
        Save Vote and grant permissions
        """
        super().save(**kwargs)
        self.grant_permissions()

    def clean(self):
        """
        Add some basic sanity checks:
        - Make sure there is no conflict before saving
        - Make sure the vote falls inside the limits of the Rating
        """
        # we might not have a review yet, in case this is a save(commit=False)
        if hasattr(self, "review"):
            if self.rating.category != self.review.item.category:
                raise ValidationError(
                    "The rating %s belongs to a different Category than the Item %s"
                    % (self.rating, self.review.item)
                )

        if self.vote > self.rating.max_rating:
            raise ValidationError(
                "The Rating must be between 0 and %s" % self.rating.max_rating
            )

    def __str__(self):
        return "Vote %s for Rating %s from Review %s for Item %s by Actor %s" % (
            self.vote,
            self.rating,
            self.review,
            self.review.item,
            self.review.actor,
        )

    @property
    def detail_url_kwargs(self):
        return (
            {
                "team_slug": self.item.category.team.slug,
                "category_slug": self.item.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.review.uuid,
                "vote_uuid": self.uuid,
            },
        )

    object_url_namespace = "team:category:item:review:vote"

    def get_absolute_url(self):
        return reverse_lazy(
            self.object_url_namespace + ":detail", kwargs=self.detail_url_kwargs
        )
