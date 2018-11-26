from django import template
from django.utils.safestring import mark_safe
register = template.Library()

from rating.models import Rating

@register.simple_tag(takes_context=True)
def get_rating(context, item, rating, actor=None, only_latest=False, html=False):
    average_rating = item.get_rating(
        rating=rating,
        actor=actor,
        only_latest=only_latest,
        ratingtype=ratingtype,
    )

    if html and rating:
        output = ''
        stars = 0
        # add stars
        for i in range(1, int(rating)+1):
            output += "<i class='fas fa-star text-success'></i>"
            stars += 1

        # add a half star?
        if round(rating-i) == 1:
            output += "<i class='fas fa-star-half-alt text-success'></i>"
            stars += 1

        # add missing stars?
        if stars < property.max_rating:
            for j in range(1, (property.max_rating+1)-stars):
                output += "<i class='fas fa-star text-muted'></i>"

        return mark_safe(output)
    else:
        # just return the numeric rating
        return rating

@register.simple_tag
def get_rating_count(item, property):
    return item.ratings.filter(property=property).count()

