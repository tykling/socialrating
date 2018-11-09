from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy

from utils.models import BaseModel


class TeamRelatedModel(BaseModel):
    """
    An abstract model on which all Team related models are based
    If a Team related model has no direct FK to Team, then the property 'team_filter' must be set on the model class.
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

    name = models.CharField(
        max_length=128,
        help_text='The name of the Team'
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
        related_name='memberships',
        help_text='The current members of this Team',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('team:detail', kwargs={'team_slug': self.slug})

    def save(self, **kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(**kwargs)


class Membership(BaseModel):
    """
    The m2m through model which links User and Team together
    """
    actor = models.ForeignKey(
        'actor.Actor',
        on_delete=models.PROTECT,
        help_text='The Actor to which this Membership belongs',
    )

    team = models.ForeignKey(
        'team.Team',
        on_delete=models.PROTECT,
        help_text='The Group to which this Membership belongs',
    )

    admin = models.BooleanField(
        default=False,
        help_text='This member is an admin of this Team'
    )

    def __str__(self):
        return "%s is %s of team %s" % (self.actor.user.username, "an admin" if self.admin else "a member", self.team.name)

