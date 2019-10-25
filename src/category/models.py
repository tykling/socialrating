import eav
import logging

from django.db import models
from django.urls import reverse_lazy
from guardian.shortcuts import assign_perm

from team.models import TeamRelatedModel
from .eavconfig import CategoryEavConfig

logger = logging.getLogger("socialrating.%s" % __name__)


class Category(TeamRelatedModel):
    """
    A category defines a type of thing/place/event. A Category belongs to a Team.
    """

    class Meta:
        ordering = ["weight", "name"]
        unique_together = [["name", "team"], ["slug", "team"]]
        permissions = (
            ("add_item", "Add Item belonging to this Category"),
            ("add_fact", "Add Fact for this Category"),
            ("add_rating", "Add Rating for this Category"),
        )

    team = models.ForeignKey(
        "team.Team",
        related_name="categories",
        on_delete=models.CASCADE,
        help_text="The Team to which this Category belongs",
    )

    name = models.CharField(
        max_length=100,
        help_text="The plural name of this Category. Must be unique within the Team. Changing the name also changes the URL slug, which means old links will stop working.",
    )

    slug = models.SlugField(
        max_length=100,
        help_text="The slug for this Category. Must be unique within the Team.",
    )

    description = models.TextField(
        help_text="The description of this category. Markdown is supported."
    )

    weight = models.IntegerField(
        default=10,
        help_text="Change the weight of a Category to change sorting. Heavier Categories sink to the bottom. Categories with the same weight are sorted by name.",
    )

    default_context = models.ForeignKey(
        "context.Context",
        on_delete=models.PROTECT,
        help_text="The default Context for new Reviews for Items in this Category. Leave blank to have no default.",
        null=True,
        blank=True,
    )

    filterfield = "team"
    filtervalue = "team"
    breadcrumb_list_name = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy(
            "team:category:detail",
            kwargs={"team_slug": self.team.slug, "category_slug": self.slug},
        )

    def grant_permissions(self):
        """
        - All team members may view a Category
        - Admins may update a Category
        - Admins may delete a Category
        - All team members may create new Items in the Category
        - Admins may create Facts for the Category
        - Admins may create Ratings for the Category
        """
        assign_perm("category.view_category", self.team.group, self)
        assign_perm("category.change_category", self.team.admingroup, self)
        assign_perm("category.delete_category", self.team.admingroup, self)
        assign_perm("category.add_item", self.team.group, self)
        assign_perm("category.add_fact", self.team.admingroup, self)
        assign_perm("category.add_rating", self.team.admingroup, self)

    def save(self, **kwargs):
        """
        Create/update slug and save the Fact and finally grant permissions.
        """
        super().save(**kwargs)
        self.grant_permissions()

    def create_fact_slug(self, fact_name):
        """
        Use the EavSlugField.create_slug_from_name to convert the name
        to a format which can be used as a valid Django field name
        """
        return eav.fields.EavSlugField.create_slug_from_name(fact_name)

    @property
    def review_count(self):
        from review.models import Review

        return Review.objects.filter(item__category=self).count()

    @property
    def vote_count(self):
        from vote.models import Vote

        return Vote.objects.filter(review__item__category=self).count()

    @property
    def attachment_count(self):
        from attachment.models import Attachment

        return Attachment.objects.filter(review__item__category=self).count()


# register Category model with django-eav2
eav.register(Category, CategoryEavConfig)
