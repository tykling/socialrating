import eav

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist

from team.models import TeamRelatedModel


class Item(TeamRelatedModel):
    """
    An Item is a thing/place/event based on a Category.
    The Category defines which attributes any given item has.
    """
    class Meta:
        ordering = ['name']
        unique_together = [['name', 'category'], ['slug', 'category']]

    category = models.ForeignKey(
        'category.Category',
        on_delete=models.PROTECT,
        related_name='items',
        help_text='The Category on which this Item is based',
    )

    name = models.CharField(
        max_length=100,
        help_text='The name of this Item. Must be unique within the Category.'
    )

    slug = models.SlugField(
        help_text='The slug for this Item. Must be unique within the Category.',
    )

    team_filter = 'category__team'

    def __str__(self):
        return "%s (Category: %s)" % (self.name, self.category)

    def get_absolute_url(self):
        return reverse_lazy('team:category:item:detail', kwargs={
            'team_slug': self.category.team.slug,
            'category_slug': self.category.slug,
            'item_slug': self.slug,
        })

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super().save(**kwargs)

    def get_rating(self, property, ratingtype, actor=None):
        if ratingtype=='average':
            return round(self.ratings.filter(property=property).aggregate(models.Avg('rating'))['rating__avg'], 2)
        elif ratingtype=='user':
            try:
                return self.ratings.get(property=property, actor=actor).rating
            except ObjectDoesNotExist:
                return None

class ItemEavConfig(eav.registry.EavConfig):
     @classmethod
     def get_attributes(cls, entity):
         """
         Items have no attributes directly, so we return the Attributes which apply to the Category of this Item
         """
         return entity.category.eav.get_all_attributes()

# register Item model with eav
eav.register(Item, ItemEavConfig)

