import logging

from django import template
from django.utils.safestring import mark_safe

from vote.models import Vote
from item.models import Item

logger = logging.getLogger("socialrating.%s" % __name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def get_average_vote(context, item, rating):
    """
    Template tag to return the averate Vote for the specified Rating
    """
    return item.get_average_vote(rating)


@register.simple_tag(takes_context=True)
def get_latest_review(context, item):
    """
    Template tag to return latest Review by the current user for the Item
    """
    if item.reviews.filter(actor=context.request.user.actor).exists():
        return item.reviews.filter(actor=context.request.user.actor).latest("created")
    else:
        return None


@register.simple_tag(takes_context=True)
def get_actor_vote(context, item, rating):
    """
    Template tag to return the latest vote for this actor.
    """
    result = item.get_actor_vote(rating=rating, actor=context.request.user.actor)
    if result:
        # a vote is always an integer, no need for .0
        return int(result)
    return None


@register.filter
def stars(obj, rating=None):
    """
    This template filter returns HTML showing "stars" based on the object.
    If obj is a Vote return stars based on that vote alone.
    If obj is an Item return average vote for the Item for the Rating.
    If obj is an int use that for the vote and get max_rating from Rating
    """
    if not obj:
        return None

    output = ""
    stars = 0
    if isinstance(obj, Vote):
        vote = obj.vote
        max_rating = obj.rating.max_rating
        icon = obj.rating.icon
    elif isinstance(obj, Item):
        vote = obj.get_average_vote(rating=rating)[0]
        max_rating = rating.max_rating
        icon = rating.icon
    elif isinstance(obj, (int, float)):
        vote = obj
        max_rating = rating.max_rating
        icon = rating.icon
    else:
        logger.error("Unsupported datatype for templatetag stars: %s" % type(obj))
        return False

    # add full stars
    for i in range(1, int(vote) + 1):
        output += "<i class='%s text-success'></i>" % icon
        stars += 1

    # add a half star?
    if round(vote - i) == 1:
        output += "<i class='%s-half-alt text-success'></i>" % icon
        stars += 1

    # add missing stars?
    if stars < max_rating:
        for j in range(1, (max_rating + 1) - stars):
            output += "<i class='%s text-muted'></i>" % icon

    return mark_safe(output)


@register.filter
def votes(item, rating):
    """
    Return the number of Votes for the Rating for that Item
    """
    return Vote.objects.filter(review__item=item, rating=rating).count()
