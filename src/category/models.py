import eav

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy

from team.models import TeamRelatedModel

class Category(TeamRelatedModel):
    """
    A category defines a type of thing/place/event. A Category belongs to a Team.
    Team owners can create, modify, and delete categories.
    """
    class Meta:
        ordering = ['name']
        unique_together = [['name', 'team'], ['slug', 'team']]

    team = models.ForeignKey(
        'team.Team',
        related_name='categories',
        on_delete=models.PROTECT,
        help_text='The Team to which this Category belongs',
    )

    name = models.CharField(
        max_length=100,
        help_text='The name of this Category. Must be unique within the Team.',
    )

    slug = models.SlugField(
        help_text='The slug for this Category. Must be unique within the Team.',
    )

    description = models.TextField(
        help_text='The description of this category. Markdown is supported.',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.slug
        })

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super().save(**kwargs)

    def create_attribute_slug(self, attribute_name):
        """
        Use the EavSlugField.create_slug_from_name to convert the name (including
        category id to make them unique) to a format which can be used as a Django field name
        """
        return eav.fields.EavSlugField.create_slug_from_name("category%s_%s" % (self.pk, attribute_name))

# register models with eav
eav.register(Category)

