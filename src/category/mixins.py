import logging

from django.shortcuts import get_object_or_404, reverse
from django.core.exceptions import PermissionDenied
from guardian.core import ObjectPermissionChecker

from team.mixins import TeamMixin

from .models import Category

logger = logging.getLogger("socialrating.%s" % __name__)


class CategoryMixin(TeamMixin):
    """
    The CategoryMixin sets self.category based on category_slug,
    checks if the user has permissions to view the category,
    and adds breadcrumbs
    """

    def setup(self, *args, **kwargs):
        # call super() now so TeamMixin runs first
        super().setup(*args, **kwargs)
        self.category = get_object_or_404(
            Category, team=self.team, slug=self.kwargs["category_slug"]
        )

        # check permissions
        if not self.request.user.has_perm("category.view_category", self.category):
            raise PermissionDenied

        # add breadcrumb for category list
        self.breadcrumbs.append(
            (
                Category.breadcrumb_list_name,
                reverse("team:category:list", kwargs={"team_slug": self.team.slug}),
            )
        )

        # add breadcrumb for this category
        self.breadcrumbs.append((self.category.name, self.category.get_absolute_url()))

        # only if this mixin is the leftmost
        if self.__class__.__mro__[1].__module__ == "category.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Category to context
        """
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["category_perms"] = ObjectPermissionChecker(
            self.request.user
        ).get_perms(self.category)
        return context
