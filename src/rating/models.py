from django.db import models
from django.template.defaultfilters import slugify

from team.models import TeamRelatedModel


class Property(TeamRelatedModel):
    """
    A Property is some subjective aspect of a Category - not facts, peoples opinions.
    Every Property describes something which can be rated by users.
    For example, a property of a concert venue might be "Sound Quality".
    """
    class Meta:
        ordering = ['name']
        unique_together = [['name', 'category'], ['slug', 'category']]

    category = models.ForeignKey(
        'category.Category',
        on_delete=models.PROTECT,
        related_name='properties',
        help_text='The Category on which this Item is based',
    )

    name = models.CharField(
        max_length=100,
        help_text='The name of this Property. Must be unique within the Category.'
    )

    slug = models.SlugField(
        help_text='The slug for this Property. Must be unique within the Category.',
    )

    description = models.CharField(
        max_length=255,
        help_text='A short description of this Property, 255 characters or less.',
    )

    max_rating = models.PositiveIntegerField(
        help_text='The maximum rating (number of stars) for this Property. Defaults to 5, maximum 100.',
        default=5,
    )

    icon = models.CharField(
        max_length=50,
        default='fas fa-star',
        help_text='The icon to use when visually displaying the ratings for this Property',
    )

    team_filter = 'category__team'

    def __str__(self):
        return "Property %s (Category: %s)" % (self.name, self.category)

    def get_absolute_url(self):
        return reverse_lazy('team:category:property:detail', kwargs={
            'team_slug': self.category.team.slug,
            'category_slug': self.category.slug,
            'property_slug': self.slug,
        })

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super().save(**kwargs)

    def clean(self):
        if self.max_rating < 2 or self.max_rating > 100:
            raise ValidationError("Max. rating must be between 2 and 100")


class Rating(TeamRelatedModel):
    """
    A Rating contains a reference to a Review and a Property,
    as well as the actual rating of course.
    It may also optionally contain a short comment.
    """
    class Meta:
        ordering = ['id']
        unique_together = [['item', 'actor', 'property']]

    item = models.ForeignKey(
        'item.Item',
        on_delete=models.PROTECT,
        related_name='ratings',
        help_text='The Item this Rating applies to',
    )

    actor = models.ForeignKey(
        'actor.Actor',
        on_delete=models.PROTECT,
        related_name='ratings',
        help_text='The Actor who made this Rating',
    )

    property = models.ForeignKey(
        'rating.Property',
        on_delete=models.PROTECT,
        related_name='ratings',
        help_text='The Property this Rating applies to',
    )

    rating = models.PositiveIntegerField(
        help_text='The rating for this Property'
    )

    comment = models.CharField(
        max_length=255,
        help_text='An optional short comment related to this specific rating. 255 character limit.',
        blank=True,
    )

    team_filter = 'review__item__category__team'

    def clean(self):
        """
        - Make sure there is no conflict before saving
        - Make sure the rating falls inside the limits of the Property
        """
        if self.item.category != self.property.category:
            raise ValidationError("The property %s belongs to a different Category than the Item %s" % (
                self.property,
                self.review.item
            ))

        if self.rating > self.property.max_rating:
            raise ValidationError("The Rating must be between 0 and %s" % self.property.max_rating)

    def __str__(self):
        return "Rating %s for Item %s Property %s by Actor %s" % (
            self.rating,
            self.item,
            self.property,
            self.actor
        )

