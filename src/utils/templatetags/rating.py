from django import template
from django.utils.safestring import mark_safe
register = template.Library()

from rating.models import Rating

@register.simple_tag
def get_average_vote(item, rating):
    """
    Template tag to return the average vote across all actors.
    Only includes the latest vote by each user.
    """
    return item.get_average_vote(
        rating=rating,
    )


@register.simple_tag(takes_context=True)
def get_actor_vote(context, item, rating):
    """
    Template tag to return the latest vote for this actor.
    """
    result = item.get_actor_vote(
        rating=rating,
        actor=context.request.user.actor,
    )
    if result:
        # a vote is always an integer, no need for .0
        return int(result)
    return None


@register.filter
def stars(rating, max_rating):
    """
    This template filter returns HTML showing "stars" based on
    rating and max_rating.
    """
    if not rating or not max_rating:
        return None

    output = ''
    stars = 0

    # add full stars
    for i in range(1, int(rating)+1):
        output += "<i class='fas fa-star text-success'></i>"
        stars += 1

    # add a half star?
    if round(rating-i) == 1:
        output += "<i class='fas fa-star-half-alt text-success'></i>"
        stars += 1

    # add missing stars?
    if stars < max_rating:
        for j in range(1, (max_rating+1)-stars):
            output += "<i class='fas fa-star text-muted'></i>"

    return mark_safe(output)

