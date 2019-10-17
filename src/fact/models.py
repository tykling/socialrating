from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from django.db import models
from eav.models import Attribute
from guardian.shortcuts import get_perms, assign_perm

from category.models import Category


class Fact(Attribute):
    """
    Fact is just another name for eav Attributes.
    We use this model with inheritance from Attribute so we can add some stuff.
    """

    category = models.ForeignKey(
        "category.Category",
        on_delete=models.CASCADE,
        related_name="facts",
        help_text="The Category to which this Fact belongs",
    )

    object_category = models.ForeignKey(
        "category.Category",
        on_delete=models.CASCADE,
        related_name="object_facts",
        null=True,
        blank=True,
        help_text="Related Category for Facts of type 'object'",
    )

    breadcrumb_list_name = "Facts"

    @property
    def team(self):
        return self.category.team

    def get_absolute_url(self):
        return reverse_lazy(
            "team:category:fact:detail",
            kwargs={
                "team_slug": self.team.slug,
                "category_slug": self.category.slug,
                "fact_slug": self.slug,
            },
        )

    def grant_permissions(self):
        """
        - All team members may view a Fact
        - Admins may update a Fact
        - Admins may delete a Fact
        """
        assign_perm("fact.view_fact", self.team.group, self)
        assign_perm("fact.change_fact", self.team.admingroup, self)
        assign_perm("fact.delete_fact", self.team.admingroup, self)
        print("done assigning permissions for fact %s" % self)

    def save(self, **kwargs):
        """
        Grant permissions after super() saving
        """
        super().save(**kwargs)
        self.grant_permissions()
