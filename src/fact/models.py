from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from eav.models import Attribute
from guardian.shortcuts import get_perms, assign_perm

from category.models import Category


class Fact(Attribute):
    """
    Fact is just another name for eav Attributes.
    We use this proxy model instead of using Attributes directly.
    """

    class Meta:
        proxy = True

    breadcrumb_list_name = "Facts"

    @property
    def category(self):
        # return self.entity_fk
        return Category.objects.get(id=self.entity_id)

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
        assign_perm("attribute.view_attribute", self.team.group, self)
        assign_perm("attribute.change_attribute", self.team.admingroup, self)
        assign_perm("attribute.delete_attribute", self.team.admingroup, self)
        print("done assigning facts for %s" % self)

    def save(self, **kwargs):
        """
        Grant permissions after super() saving
        """
        super().save(**kwargs)
        self.grant_permissions()
