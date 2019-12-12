from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter
def tags(obj):
    output = ""
    if obj.tags.exists():
        for tag in obj.tags.all():
            output += "<span class='badge badge-primary'>%s</span> " % escape(tag.name)
    return mark_safe(output)
