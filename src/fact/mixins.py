import logging


from django.shortcuts import get_object_or_404, reverse
from django.contrib.contenttypes.models import ContentType

from category.mixins import CategorySlugMixin
from .models import Fact

logger = logging.getLogger("socialrating.%s" % __name__)


class FactSlugMixin(CategorySlugMixin):
    """
    The FactSlugMixin sets self.fact based on fact_slug from the URL,
    and also sets breadcrumbs.
    Inherits from CategoryMixin so we also have self.category available
    """

    def setup(self, *args, **kwargs):
        # call super() now so CategorySlugMixin runs first
        super().setup(*args, **kwargs)
        self.fact = get_object_or_404(
            Fact, category=self.category, slug=self.kwargs["fact_slug"]
        )
        # check permissions
        if not self.request.user.has_perm("fact.view_fact", self.fact):
            raise PermissionDenied

        # add breadcrumb for Fact list
        self.breadcrumbs.append(
            (
                "Facts",
                reverse(
                    "team:category:fact:list",
                    kwargs={
                        "team_slug": self.team.slug,
                        "category_slug": self.category.slug,
                    },
                ),
            )
        )

        # add breadcrumb for this Fact
        self.breadcrumbs.append((self.fact.name, self.fact.get_absolute_url()))

        # only if this mixin is the leftmost, add self.breadcrumb_title too (if we have one)
        if self.__class__.__mro__[1].__module__ == "fact.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Fact to context
        """
        context = super().get_context_data(**kwargs)
        context["fact"] = self.fact
        return context
