import logging

from django.shortcuts import get_object_or_404, reverse
from django.core.exceptions import PermissionDenied
from guardian.core import ObjectPermissionChecker

from category.mixins import CategoryMixin
from .models import Rating

logger = logging.getLogger("socialrating.%s" % __name__)


class RatingMixin(CategoryMixin):
    """
    The RatingMixin sets self.rating based on rating_slug from the URL,
    and also sets breadcrumbs.
    Inherits from CategoryMixin so we also have self.category available
    """

    def setup(self, *args, **kwargs):
        # call super() now so CategoryMixin runs first
        super().setup(*args, **kwargs)
        self.rating = get_object_or_404(
            Rating, category=self.category, slug=self.kwargs["rating_slug"]
        )

        # check permissions
        if not self.request.user.has_perm("rating.view_rating", self.rating):
            raise PermissionDenied

        # add breadcrumb for rating list
        self.breadcrumbs.append(
            (
                Rating.breadcrumb_list_name,
                reverse(
                    "team:category:rating:list",
                    kwargs={
                        "team_slug": self.team.slug,
                        "category_slug": self.category.slug,
                    },
                ),
            )
        )
        # add breadcrumb for this Rating
        self.breadcrumbs.append((self.rating.name, self.rating.get_absolute_url()))

        # only if this mixin is the leftmost
        if self.__class__.__mro__[1].__module__ == "rating.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Rating to context
        """
        context = super().get_context_data(**kwargs)
        context["rating"] = self.rating
        context["rating_perms"] = ObjectPermissionChecker(self.request.user).get_perms(
            self.rating
        )
        return context
