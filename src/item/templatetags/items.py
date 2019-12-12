import logging

from django import template

from item.models import Item
from fact.models import Fact
from eav.models import Value

logger = logging.getLogger("socialrating.%s" % __name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def get_related_items(context):
    """
    Template tag to return a list of querysets with the related items
    """
    result = []
    for related_fact in Fact.objects.filter(object_category=context["category"]):
        result.append(
            Item.objects.filter(
                uuid__in=Value.objects.filter(
                    generic_value_id=context["item"].uuid, attribute=related_fact
                ).values_list("entity_id", flat=True)
            )
        )
    return result
