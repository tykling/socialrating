from django.db import models

from team.models import TeamRelatedModel


class Review(TeamRelatedModel):
    """
    A Review is linked to an Actor and an Item.
    All Ratings are linked to a Review.
    """
    class Meta:
        ordering = ['id']
        unique_together = [['actor', 'item']]

    actor = models.ForeignKey(
        'actor.Actor',
        on_delete=models.PROTECT,
        related_name='reviews',
        help_text='The Actor who made this Review',
    )

    item = models.ForeignKey(
        'item.Item',
        on_delete=models.PROTECT,
        related_name='reviews',
        help_text='The Item this Review applies to',
    )

    review = models.TextField(
        help_text='The review of this Item',
        blank=True,
    )

    team_filter = 'item__category__team'

    def __str__(self):
        return "Review for Item %s by Actor %s" % (
            self.item,
            self.actor
        )

