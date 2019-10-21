import logging

from django.shortcuts import get_object_or_404, reverse
from django.core.exceptions import PermissionDenied
from guardian.core import ObjectPermissionChecker

from item.mixins import ItemMixin
from .models import Review

logger = logging.getLogger("socialrating.%s" % __name__)


class ReviewMixin(ItemMixin):
    """
    The ReviewMixin sets self.review based on review_uuid from the URL,
    also sets breadcrumbs and checks permissions.
    Inherits from ItemMixin so we also have self.item available
    """

    def setup(self, *args, **kwargs):
        # call super() now so ItemMixin runs first
        super().setup(*args, **kwargs)
        self.review = get_object_or_404(
            Review, item=self.item, uuid=self.kwargs["review_uuid"]
        )

        # check permissions
        if not self.request.user.has_perm("review.view_review", self.review):
            raise PermissionDenied

        # add breadcrumb for review list
        self.breadcrumbs.append(
            (
                Review.breadcrumb_list_name,
                reverse(
                    "team:category:item:review:list",
                    kwargs={
                        "team_slug": self.team.slug,
                        "category_slug": self.category.slug,
                        "item_slug": self.item.slug,
                    },
                ),
            )
        )

        # add breadcrumb for this review
        if len(self.review.headline) > 30:
            headline = self.review.headline[:27] + "..."
        else:
            headline = self.review.headline
        self.breadcrumbs.append((headline, self.review.get_absolute_url()))

        # only if this mixin is the leftmost
        if self.__class__.__mro__[1].__module__ == "review.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Review to context
        """
        context = super().get_context_data(**kwargs)
        context["review"] = self.review
        context["review_perms"] = ObjectPermissionChecker(self.request.user).get_perms(
            self.review
        )
        return context
