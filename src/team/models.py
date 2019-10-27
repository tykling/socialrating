import logging

from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

from utils.models import UUIDBaseModel
from actor.models import Actor

logger = logging.getLogger("socialrating.%s" % __name__)


class Team(UUIDBaseModel):
    """
    Everything belongs to a Team
    """

    class Meta:
        ordering = ["name"]
        permissions = (
            ("add_category", "Add Category belonging to this Team"),
            ("add_context", "Add Context belonging to this Team"),
        )

    group = models.OneToOneField(
        Group,
        help_text="The Django Group for all members of this Team",
        on_delete=models.PROTECT,
        related_name="team",
    )

    admingroup = models.OneToOneField(
        Group,
        help_text="The Django Group for admin members of this Team",
        on_delete=models.PROTECT,
        related_name="adminteam",
    )

    name = models.CharField(
        max_length=128, help_text="The name of the Team. Make it short and memorable."
    )

    description = models.TextField(help_text="A short description of this team.")

    slug = models.SlugField(unique=True, help_text="The slug for this Team")

    founder = models.ForeignKey(
        "actor.Actor",
        related_name="founded_teams",
        on_delete=models.PROTECT,
        help_text="The founder of this Team",
    )

    members = models.ManyToManyField(
        "actor.Actor",
        through="team.Membership",
        related_name="teams",
        help_text="The current members of this Team",
    )

    breadcrumb_list_name = "Teams"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("team:detail", kwargs={"team_slug": self.slug})

    def grant_permissions(self):
        """
        - All team members may view the Team
        - Admins may change the Team
        - Admins may delete the Team
        - Admins may create a new Category
        - Admins may create a new Context
        """
        assign_perm("team.view_team", self.group, self)
        assign_perm("team.change_team", self.admingroup, self)
        assign_perm("team.delete_team", self.admingroup, self)
        assign_perm("team.add_category", self.admingroup, self)
        assign_perm("team.add_context", self.admingroup, self)

    def create_django_groups(self):
        # create group
        self.group = Group.objects.create(name=self.name)
        # create admingroup
        self.admingroup = Group.objects.create(name=self.name + " Admins")

    def add_founder_membership(self):
        # add founder as an admin team member
        Membership.objects.create(actor=self.founder, team=self, admin=True)

    def save(self, **kwargs):
        if self._state.adding:
            adding = True
            # create django groups as needed before saving
            self.create_django_groups()
        else:
            adding = False
        # save team
        super().save(**kwargs)
        # is this a new team?
        if adding:
            # this is a new team, add founder as member
            self.add_founder_membership()
            # and grant Team permissions
            self.grant_permissions()

    @property
    def adminmembers(self):
        return Actor.objects.filter(memberships__team=self, memberships__admin=True)

    @property
    def items(self):
        """
        Return a queryset of all Items belonging to this Team
        """
        from item.models import Item

        return Item.objects.filter(category__team=self)

    @property
    def reviews(self):
        """
        Return a queryset of all Reviews belonging to this Team
        """
        from review.models import Review

        return Review.objects.filter(item__category__team=self)

    @property
    def attachments(self):
        """
        Return a queryset of all Attachments belonging to this Team
        """
        from attachment.models import Attachment

        return Attachment.objects.filter(review__item__category__team=self)

    @property
    def facts(self):
        """
        Return a queryset of all Facts belonging to this team.
        """
        from fact.models import Fact

        return Fact.objects.filter(category__team=self)

    @property
    def ratings(self):
        """
        Return a queryset of all Ratings belonging to this team.
        """
        from rating.models import Rating

        return Rating.objects.filter(category__team=self)

    @property
    def votes(self):
        """
        Return a queryset of all Votes belonging to this team.
        """
        from vote.models import Vote

        return Vote.objects.filter(rating__category__team=self)


class Membership(UUIDBaseModel):
    """
    The m2m through model which links Actor and Team together
    """

    class Meta:
        unique_together = [("actor", "team")]

    actor = models.ForeignKey(
        "actor.Actor",
        on_delete=models.PROTECT,
        help_text="The Actor to which this Membership belongs",
        related_name="memberships",
    )

    team = models.ForeignKey(
        "team.Team",
        on_delete=models.CASCADE,
        help_text="The Group to which this Membership belongs",
        related_name="memberships",
    )

    admin = models.BooleanField(
        default=False, help_text="This member is an admin of this Team"
    )

    def __str__(self):
        return "%s is %s of team %s" % (
            self.actor.user.username,
            "an admin" if self.admin else "a member",
            self.team.name,
        )

    def fix_group_memberships(self):
        """
        Fix Django group memberships based on this group membership
        """
        if not self.actor.user.groups.filter(name=self.team.group.name).exists():
            self.actor.user.groups.add(self.team.group)

        if (
            self.admin
            and not self.actor.user.groups.filter(
                name=self.team.admingroup.name
            ).exists()
        ):
            self.actor.user.groups.add(self.team.admingroup)

    def save(self, **kwargs):
        """
        Create Django group memberships to match this Team membership
        """
        super().save(**kwargs)
        self.fix_group_memberships()
