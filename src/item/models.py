import eav
import logging

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist

from team.models import TeamRelatedModel

logger = logging.getLogger("socialrating.%s" % __name__)


class Item(TeamRelatedModel):
    """
    An Item is a thing/place/event based on a Category.
    The Category defines which Facts and Ratings any given item has.
    """
    class Meta:
        ordering = ['name']
        unique_together = [['name', 'category'], ['slug', 'category']]

    category = models.ForeignKey(
        'category.Category',
        on_delete=models.CASCADE,
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
        """
        Update the slug of the Item
        """
        self.slug = slugify(self.name)
        super().save(**kwargs)

    def get_rating(self, rating, actor=None, only_latest=True):
        """
        Get the average Vote for a given Rating for this Item.
        Optionally limit to reviews from only one Actor by passing an Actor object.
        Set only_latest=False to include all reviews. By default only the latest review from each Actor is considered. 
        """
        # First get all Reviews for this Item
        reviews = self.reviews.all().order_by('actor', 'created')
        logger.debug("Found %s reviews of item %s" % reviews.count())

        # Do we only want a specific Actor?
        if actor:
            reviews = reviews.filter(actor=actor)
            logger.debug("Filtered reviews by actor, we have %s reviews now" % reviews.count())

        # Are we only considering the latest Review from each Actor? 
        if only_latest:
            reviews = reviews.distinct('actor')
            logger.debug("Including only the latest Review from each Actor, we have %s reviews now" % reviews.count())

        # Get the Votes
        votes = Vote.objects.filter(rating=rating, review__in=reviews)
        logger.debug("Found %s Votes for Rating %s in the %s Reviews considered" % (votes.count, rating, reviews.count()))
        if not votes:
            return None

        # return a rounded average
        result = round(votes.aggregate(models.Avg('vote'))['vote__avg'], 2)
        logger.debug("Returning result %s" % result)
        return result

    @property
    def facts(self):
        """
        We use the term "fact" to describe some aspect of an Item which is indisputable.
        It is just another word for EAV attributes.
        """
        return self.eav.get_all_attributes()


class ItemEavConfig(eav.registry.EavConfig):
     @classmethod
     def get_attributes(cls, entity):
         """
         Items have no EAV attributes directly, so we return the 
         Attributes which apply to the Category of this Item.
         """
         return entity.category.eav.get_all_attributes()

# register Item model with django-eav2
eav.register(Item, ItemEavConfig)

