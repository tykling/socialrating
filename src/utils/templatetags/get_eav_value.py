from django import template
register = template.Library()

@register.filter
def get_eav_value(obj, attribute):
    return getattr(obj.eav, attribute)

