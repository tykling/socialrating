import logging

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from guardian.shortcuts import get_perms, assign_perm

from utils.models import BaseModel, UUIDBaseModel

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamRelatedModel(BaseModel):
    """
    An abstract model on which all Team related models are based
    If a Team related model has no direct FK to Team, then the 
    property 'team_filter' must be set on the model class.
    """
    team_filter = 'team'

    class Meta:
        abstract = True

    @classmethod
    def get_team_filter(cls):
        return cls.team_filter


class TeamRelatedUUIDModel(UUIDBaseModel):
    """
    This is identical to TeamRelatedModel but inherits
    from UUIDBaseModel instead of BaseModel
    """
    team_filter = 'team'

    class Meta:
        abstract = True

    @classmethod
    def get_team_filter(cls):
        return cls.team_filter


class Team(BaseModel):
    """
    Everything belongs to a Team
    """
    class Meta:
        ordering = ['name']

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
        max_length=128,
        help_text='The name of the Team. Make it short and memorable.'
    )

    description = models.TextField(
        help_text='A short description of this team.',
    )

    slug = models.SlugField(
        unique=True,
        help_text='The slug for this Team',
    )

    founder = models.ForeignKey(
        'actor.Actor',
        related_name='founded_teams',
        on_delete=models.PROTECT,
        help_text='The founder of this Team',
    )

    members = models.ManyToManyField(
        'actor.Actor',
        through='team.Membership',
        related_name='teams',
        help_text='The current members of this Team',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('team:detail', kwargs={'team_slug': self.slug})

    def save(self, **kwargs):
        # create slug if we have none
        if not self.slug:
            self.slug=slugify(self.name)

        if not self.pk:
            # this is a new Team, create django groups
            self.group = Group.objects.create(name=self.name)
            self.admingroup = Group.objects.create(name=self.name + " Admins")

        # ok, save
        super().save(**kwargs)

        # fix team.view_team permission if needed
        if not 'team.view_team' in get_perms(self.group, self):
            assign_perm('team.view_team', self.group, self)

        # fix team.change_team permission if needed
        if not 'team.change_team' in get_perms(self.admingroup, self):
            assign_perm('team.change_team', self.admingroup, self)

        # fix team.delete_team permission if needed
        if not 'team.delete_team' in get_perms(self.admingroup, self):
            assign_perm('team.delete_team', self.admingroup, self)


class Membership(BaseModel):
    """
    The m2m through model which links Actor and Team together
    """
    actor = models.ForeignKey(
        'actor.Actor',
        on_delete=models.PROTECT,
        help_text='The Actor to which this Membership belongs',
        related_name='memberships',
    )

    team = models.ForeignKey(
        'team.Team',
        on_delete=models.PROTECT,
        help_text='The Group to which this Membership belongs',
        related_name='memberships',
    )

    admin = models.BooleanField(
        default=False,
        help_text='This member is an admin of this Team'
    )

    def __str__(self):
        return "%s is %s of team %s" % (self.actor.user.username, "an admin" if self.admin else "a member", self.team.name)

    def save(self, **kwargs):
        """
        Create Django group memberships to match this Team membership
        """
        if not self.actor.user.groups.filter(name=self.team.group.name).exists():
            # add the user to django group
            logger.debug("Adding user %s to group %s" % (self.actor.user, self.team.group))
            self.actor.user.groups.add(self.team.group)

        if self.admin and not self.actor.user.groups.filter(name=self.team.admingroup.name).exists():
            # add the user to django admingroup
            logger.debug("Adding user %s to admingroup %s" % (self.actor.user, self.team.admingroup))
            self.actor.user.groups.add(self.team.admingroup)

        super().save(**kwargs)

