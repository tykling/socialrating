from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy

from team.models import TeamRelatedModel, TeamRelatedUUIDModel


class Rating(TeamRelatedModel):
    """
    A Rating is some voteable aspect of a Category - peoples opinions rather than facts.
    Every Rating describes something which can be numerically rated/voted on by users.
    For example, a Rating for a "Concert Venue" might be "Sound Quality".
    """
    class Meta:
        ordering = ['name']
        unique_together = [['name', 'category'], ['slug', 'category']]

    category = models.ForeignKey(
        'category.Category',
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text='The Category on which this Item is based',
    )

    name = models.CharField(
        max_length=100,
        help_text='The name of this Rating. Must be unique within this Category.'
    )

    slug = models.SlugField(
        help_text='The slug for this Rating. Must be unique within this Category.',
    )

    description = models.CharField(
        max_length=255,
        help_text='Describe what users should consider when voting for this Rating. Please keep it to 255 characters or less.',
    )

    max_rating = models.PositiveIntegerField(
        help_text='The highest possible vote for this rating. Minimum 2, defaults to 5, maximum 100.',
        default=5,
    )

    icon = models.CharField(
        max_length=50,
        default='fas fa-star',
        help_text='The icon to use when visually displaying the votes for this rating.',
    )

    team_filter = 'category__team'

    @property
    def team(self):
        return self.category.team

    def __str__(self):
        return "Rating %s (Category: %s)" % (self.name, self.category)

    def get_absolute_url(self):
        return reverse_lazy('team:category:rating:detail', kwargs={
            'team_slug': self.category.team.slug,
            'category_slug': self.category.slug,
            'rating_slug': self.slug,
        })

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super().save(**kwargs)

    def clean(self):
        if self.max_rating < 2 or self.max_rating > 100:
            raise ValidationError("Max. rating must be between 2 and 100")


class Vote(TeamRelatedUUIDModel):
    """
    A Vote contains a reference to a Rating and a Review,
    as well as the actual Vote (a PositiveIntegerField).
    It may also optionally contain a short comment related to this specific vote.
    """
    class Meta:
        ordering = ['pk']
        unique_together = [['review', 'rating']]

    review = models.ForeignKey(
        'review.Review',
        on_delete=models.CASCADE,
        related_name='votes',
        help_text='The Review this Vote belongs to.',
    )

    rating = models.ForeignKey(
        'rating.Rating',
        on_delete=models.CASCADE,
        related_name='votes',
        help_text='The Rating this Vote applies to.',
    )

    vote = models.PositiveIntegerField(
        help_text='The actual numerical vote for this Rating.'
    )

    comment = models.CharField(
        max_length=255,
        help_text='An optional short comment related to this specific vote. 255 character limit.',
        blank=True,
        null=True,
    )

    team_filter = 'review__item__category__team'

    @property
    def team(self):
        return self.review.item.category.team

    def clean(self):
        """
        Add some basic sanity checks:
        - Make sure there is no conflict before saving
        - Make sure the rating falls inside the limits of the Property
        """
        if self.rating not in self.review.item.category.ratings.all():
            raise ValidationError("The rating %s belongs to a different Category than the Item %s" % (
                self.rating,
                self.review.item
            ))

        if self.vote > self.rating.max_rating:
            raise ValidationError("The Rating must be between 0 and %s" % self.property.max_rating)

    def __str__(self):
        return "Vote %s for Rating %s from Review %s for Item %s by Actor %s" % (
            self.vote,
            self.rating,
            self.review,
            self.review.item,
            self.review.actor,
        )

