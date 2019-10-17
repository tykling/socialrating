import logging

from django.db import models
from django.urls import reverse_lazy
from guardian.shortcuts import get_perms, assign_perm

from team.models import TeamRelatedModel

logger = logging.getLogger("socialrating.%s" % __name__)


class Context(TeamRelatedModel):
    """
    A context defines some sort of grouping of reviews.
    It might be an event, like a music festival grouping concert reviews,
    or it could be something more abstract like "caravan pulling" when reviewing a veichle.
    Team admins can create, modify, and delete contexts.
    A review must be associated with a context.
    """

    class Meta:
        ordering = ["name"]
        unique_together = [["name", "team"], ["slug", "team"]]

    team = models.ForeignKey(
        "team.Team",
        related_name="contexts",
        on_delete=models.CASCADE,
        help_text="The Team to which this Context belongs",
    )

    name = models.CharField(
        max_length=100,
        help_text="The name of this Context. Must be unique within the Team.",
    )

    slug = models.SlugField(
        help_text="The slug for this Context. Must be unique within the Team."
    )

    description = models.TextField(
        help_text="The description of this context. Markdown is supported."
    )

    breadcrumb_list_name = "Contexts"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy(
            "team:context:detail",
            kwargs={"team_slug": self.team.slug, "context_slug": self.slug},
        )

    def grant_permissions(self):
        """
        - All team members may view a Context
        - Admin members may change a Context
        - Admin members may delete a Context
        """
        assign_perm("context.view_context", self.team.group, self)
        assign_perm("context.change_context", self.team.admingroup, self)
        assign_perm("context.delete_context", self.team.admingroup, self)

    def save(self, **kwargs):
        # save the Context
        super().save(**kwargs)
        # grant permissions for the context
        self.grant_permissions()
