from django.db import models
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from guardian.shortcuts import assign_perm

from utils.models import UUIDBaseModel


class Rating(UUIDBaseModel):
    """
    A Rating is some voteable aspect of a Category - peoples opinions
    rather than facts. Every Rating describes something which can be
    numerically rated/voted on by users. For example, a Rating for a
    "Concert Venue" might be "Sound Quality".
    """

    class Meta:
        ordering = ["name"]
        unique_together = [["name", "category"], ["slug", "category"]]

    category = models.ForeignKey(
        "category.Category",
        on_delete=models.CASCADE,
        related_name="ratings",
        help_text="The Category on which this Item is based",
    )

    name = models.CharField(
        max_length=100,
        help_text="The name of this Rating. Must be unique within this Category.",
    )

    slug = models.SlugField(
        max_length=100,
        help_text="The slug for this Rating. Must be unique within this Category.",
    )

    description = models.CharField(
        max_length=255,
        help_text="Describe what users should consider when voting for this Rating. Please keep it to 255 characters or less.",
    )

    max_rating = models.PositiveIntegerField(
        help_text="The highest possible vote for this rating. Minimum 2, defaults to 5, maximum 100.",
        default=5,
    )

    icon = models.CharField(
        max_length=50,
        default="fas fa-star",
        help_text="The icon to use when visually displaying the votes for this rating.",
    )

    filterfield = "category"
    filtervalue = "category"
    breadcrumb_list_name = "Ratings"

    @property
    def team(self):
        return self.category.team

    def __str__(self):
        return "Rating %s (Category: %s)" % (self.name, self.category)

    def get_absolute_url(self):
        return reverse_lazy(
            "team:category:rating:detail",
            kwargs={
                "team_slug": self.category.team.slug,
                "category_slug": self.category.slug,
                "rating_slug": self.slug,
            },
        )

    def grant_permissions(self):
        """
        - All team members may see a vote
        - Only the Review author may change the Vote
        - Only team admins and the Review author may delete a Vote
        """
        assign_perm("rating.view_rating", self.team.group, self)
        assign_perm("rating.change_rating", self.team.admingroup, self)
        assign_perm("rating.delete_rating", self.team.admingroup, self)

    def save(self, **kwargs):
        super().save(**kwargs)
        self.grant_permissions()

    def clean(self):
        if self.max_rating < 2 or self.max_rating > 100:
            raise ValidationError("Max. rating must be between 2 and 100")
