import eav
import logging

from django.db import models
from django.urls import reverse_lazy
from guardian.shortcuts import assign_perm

from utils.models import UUIDBaseModel
from vote.models import Vote
from .eavconfig import ItemEavConfig

logger = logging.getLogger("socialrating.%s" % __name__)


class Item(UUIDBaseModel):
    """
    An Item is a thing/place/event based on a Category.
    The Category defines which Facts and Ratings any given item has.
    """

    class Meta(UUIDBaseModel.Meta):
        ordering = ["name"]
        unique_together = [["name", "category"], ["slug", "category"]]
        permissions = (
            ("add_review", "Add Review belonging to this Item"),
            ("add_comment", "Add Comment about this Item"),
            ("add_attachment", "Add Attachment for this Item"),
        )

    category = models.ForeignKey(
        "category.Category",
        on_delete=models.CASCADE,
        related_name="items",
        help_text="The Category on which this Item is based",
    )

    name = models.CharField(
        max_length=100,
        help_text="The name of this Item. Must be unique within the Category.",
    )

    description = models.TextField(
        null=True, blank=True, help_text="A description for this Item (optional)."
    )

    slug = models.SlugField(
        max_length=100,
        help_text="The slug for this Item. Must be unique within the Category.",
    )

    filterfield = "category"
    filtervalue = "category"
    breadcrumb_list_name = "Items"

    @property
    def team(self):
        return self.category.team

    def __str__(self):
        return self.name

    @property
    def detail_url_kwargs(self):
        return {
            "team_slug": self.category.team.slug,
            "category_slug": self.category.slug,
            "item_slug": self.slug,
        }

    object_url_namespace = "team:category:item"

    def get_absolute_url(self):
        return reverse_lazy(
            self.object_url_namespace + ":detail", kwargs=self.detail_url_kwargs
        )

    def grant_permissions(self):
        """
        - All team members may see an Item
        - All team members may change an Item
        - Only team admins may delete an Item
        - Also grant add_review permissions to all team members
        - Also grant add_attachment permissions to all team members
        - Also grant add_commment permissions to all team members
        """
        assign_perm("item.view_item", self.team.group, self)
        assign_perm("item.change_item", self.team.group, self)
        assign_perm("item.delete_item", self.team.admingroup, self)
        assign_perm("item.add_review", self.team.group, self)
        assign_perm("item.add_attachment", self.team.group, self)
        assign_perm("item.add_comment", self.team.group, self)

    def save(self, **kwargs):
        """
        Save the Item and grant permissions
        """
        super().save(**kwargs)
        self.grant_permissions()

    def get_average_vote(self, rating, only_latest=True):
        """
        Get the average Vote for a given Rating for this Item.
        By default only the latest Vote from each Actor is considered.
        Set only_latest=False to include multiple Votes from each actor.
        """
        votes = Vote.objects.filter(review__item=self, rating=rating).order_by()
        logger.debug(
            "Found %s votes to consider for item %s" % (votes.count(), self.name)
        )
        if only_latest:
            actors = votes.distinct("review__actor").values_list(
                "review__actor", flat=True
            )
            voteids = []
            for actor in actors:
                voteids.append(
                    Vote.objects.filter(
                        review__item=self, rating=rating, review__actor=actor
                    )
                    .latest()
                    .uuid
                )
            votes = Vote.objects.filter(uuid__in=voteids)

        logger.debug(
            "Found %s votes to consider for item %s" % (votes.count(), self.name)
        )

        if not votes:
            return (None, 0)

        # return a rounded average, manually because:
        # aggregate() + distinct(fields) not implemented.
        # TODO: check if this was added in 2.2 maybe?
        sum = 0
        for vote in votes.values_list("vote", flat=True):
            sum += vote
        result = (round(sum / votes.count(), 2), votes.count())
        logger.debug("returning %s %s" % result)
        return result

    def get_actor_vote(self, rating, actor, only_latest=True):
        """
        Get the average Vote for a given Rating for this Actor
        for this Item.
        By default only the latest Vote is considered.
        Set only_latest=False to include all Votes.
        """
        votes = Vote.objects.filter(
            review__item=self, rating=rating, review__actor=actor
        )

        if only_latest and votes:
            # just return the value of the latest vote directly
            return votes.latest("created").vote

        if not votes:
            # nothing to do here
            return None

        # return a rounded average, manually because:
        # aggregate() + distinct(fields) not implemented.
        # TODO: check if this was added in 2.2 maybe?
        sum = 0
        for vote in votes.values_list("vote", flat=True):
            sum += vote
        return round(sum / votes.count(), 2)

    @property
    def facts(self):
        """
        We use the term "fact" to describe some aspect of an Item which
        is indisputable. Fact is just another word for EAV attributes.
        """
        return self.category.facts.all()

    @property
    def ratings(self):
        return self.category.ratings.all()

    @property
    def last10reviews(self):
        return self.reviews.all()[:10]


# register Item model with django-eav2
eav.register(Item, ItemEavConfig)
