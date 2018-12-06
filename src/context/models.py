from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy

from team.models import TeamRelatedModel

class Context(TeamRelatedModel):
    """
    A context defines some sort of grouping of reviews.
    It might be an event, like a music festival grouping concert reviews,
    or it could be something more abstract like "caravan pulling" when reviewing a veichle.
    Team admins can create, modify, and delete contexts.
    A review must be associated with a context.
    """
    class Meta:
        ordering = ['name']
        unique_together = [['name', 'team'], ['slug', 'team']]

    team = models.ForeignKey(
        'team.Team',
        related_name='contexts',
        on_delete=models.PROTECT,
        help_text='The Team to which this Context belongs',
    )

    name = models.CharField(
        max_length=100,
        help_text='The name of this Context. Must be unique within the Team.',
    )

    slug = models.SlugField(
        help_text='The slug for this Context. Must be unique within the Team.',
    )

    description = models.TextField(
        help_text='The description of this context. Markdown is supported.',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('team:context:detail', kwargs={
            'team_slug': self.team.slug,
            'context_slug': self.slug
        })

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super().save(**kwargs)

