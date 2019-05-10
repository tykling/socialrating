import eav
import logging

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import get_perms, assign_perm

from team.models import TeamRelatedModel
from eventlog.models import Event
from rating.models import Vote

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

    @property
    def team(self):
        return self.category.team

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

        # fix item.view_item permission if needed 
        if not 'item.view_item' in get_perms(self.team.group, self):
            assign_perm('item.view_item', self.team.group, self)

        # fix item.add_item permission if needed 
        if not 'item.add_item' in get_perms(self.team.group, self):
            assign_perm('item.add_item', self.team.group)

        # fix item.change_item permission if needed 
        if not 'item.change_item' in get_perms(self.team.admingroup, self):
            assign_perm('item.change_item', self.team.admingroup, self)

        # fix item.delete_item permission if needed 
        if not 'item.delete_item' in get_perms(self.team.admingroup, self):
            assign_perm('item.delete_item', self.team.admingroup, self)


    def get_average_vote(self, rating, only_latest=True):
        """
        Get the average Vote for a given Rating for this Item.
        By default only the latest Vote from each Actor is considered. 
        Set only_latest=False to include multiple Votes from each actor.
        """
        votes = Vote.objects.filter(
            review__item=self,
            rating=rating,
        ).order_by('review__actor', '-created')
        logger.debug("Found %s votes to consider" % votes.count())

        if only_latest:
            votes = votes.distinct('review__actor')
            logger.debug("Including only the latest Vote from each Actor, we have %s votes now" % votes.count())

        if not votes:
            return (None, 0)

        # return a rounded average, manually because:
        # aggregate() + distinct(fields) not implemented.
        sum = 0
        for vote in votes.values_list('vote', flat=True):
            sum += vote
        print(sum, votes.count())
        return (round(sum/votes.count(), 2), votes.count())


    def get_actor_vote(self, rating, actor, only_latest=True):
        """
        Get the average Vote for a given Rating for this Actor
        for this Item.
        By default only the latest Vote is considered.
        Set only_latest=False to include all Votes.
        """
        votes = Vote.objects.filter(
            review__item=self,
            rating=rating,
            review__actor=actor,
        )

        if only_latest and votes:
            # just return the value of the latest vote directly
            return votes.latest('created').vote

        if not votes:
            # nothing to do here
            return None

        # return a rounded average, manually because:
        # aggregate() + distinct(fields) not implemented.
        sum = 0
        for vote in votes.values_list('vote', flat=True):
            sum += vote
        return round(sum/votes.count(), 2)


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

