from django.db import models
from django.core.exceptions import ValidationError

from team.models import TeamRelatedModel


class Review(TeamRelatedModel):
    """
    A Review is linked to an Actor and an Item.
    All Ratings are linked to a Review.
    """
    class Meta:
        ordering = ['id']

    actor = models.ForeignKey(
        'actor.Actor',
        on_delete=models.PROTECT,
        related_name='reviews',
        help_text='The Actor who made this Review',
    )

    item = models.ForeignKey(
        'item.Item',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='The Item this Review applies to',
    )

    context = models.ForeignKey(
        'context.Context',
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
        help_text='The Context to which this Review belongs.',
    )

    review = models.TextField(
        help_text='The text review. Optional. Markdown is supported (or will be at some point).',
        null=True,
        blank=True,
    )

    team_filter = 'item__category__team'

    def __str__(self):
        return "Review for Item %s by Actor %s" % (
            self.item,
            self.actor
        )

    def get_absolute_url(self):
        return reverse_lazy('team:category:item:review:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
            'item_slug': self.item.slug,
            'review_uuid': self.uuid,
        })

    def save(self, **kwargs):
        """
        Validate a few things
        """
        if self.item.category.requires_context and not self.context:
            raise ValidationError("You must pick a Context for Items in this Category.")

        # all good
        super().save(**kwargs)

