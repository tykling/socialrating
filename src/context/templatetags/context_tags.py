import logging

from django import template
from django.http import QueryDict
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger("socialrating.%s" % __name__)
register = template.Library()


@register.filter
def togglecontext(request, context):
    """
    Toggles context and returns the resulting url as a string
    """
    # parse the original url
    parsed_url = urlparse(request.get_full_path())
    # create a QueryDict to parse the GET params
    queries = QueryDict(parsed_url.query, mutable=True)
    # get contexts param
    contexts = queries.getlist("context")
    if contexts:
        if context.slug in contexts:
            contexts.remove(context.slug)
        else:
            contexts.append(context.slug)
        if contexts:
            queries.setlist("context", contexts)
        else:
            del queries["context"]
    else:
        queries["context"] = context.slug
    queries = queries.urlencode()
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            queries,
            parsed_url.fragment,
        )
    )
    return new_url


@register.filter
def clearcontext(request):
    """
    Removes all context GET vars from url and returns
    """
    parsed_url = urlparse(request.get_full_path())
    queries = QueryDict(parsed_url.query, mutable=True)
    if "context" in queries:
        del queries["context"]
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            queries,
            parsed_url.fragment,
        )
    )
    return new_url
