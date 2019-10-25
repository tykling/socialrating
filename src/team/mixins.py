import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import reverse
from django.core.exceptions import PermissionDenied
from guardian.core import ObjectPermissionChecker

from team.models import Team

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamMixin:
    """
    A mixin to set self.team based on team_slug from the URL,
    or return 404 if the slug was not found.
    Then check if request.user has permissions to view the team,
    and return 403 if not.
    """

    def setup(self, *args, **kwargs):
        # super setup() so we have self.request available
        super().setup(*args, **kwargs)

        # get the team or return 404
        self.team = get_object_or_404(Team, slug=kwargs["team_slug"])

        # check permissions
        if not self.request.user.has_perm("team.view_team", self.team):
            raise PermissionDenied

        # add breadcrumb for team list
        self.breadcrumbs = [((Team.breadcrumb_list_name, reverse("team:list")))]

        # add current team to breadcrumbs
        self.breadcrumbs.append((self.team.name, self.team.get_absolute_url()))

        # only if this mixin is the leftmost
        if self.__class__.__mro__[1].__module__ == "team.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Team and breadcrumbs to context
        """
        context = super().get_context_data(**kwargs)
        context["team"] = self.team
        context["team_perms"] = ObjectPermissionChecker(self.request.user).get_perms(
            self.team
        )
        return context

    def get_queryset(self):
        """
        Filter objects by their filterfield and filtervalue property.
        The filterfield holds the name of the field we want to filter by on the model,
        and filtervalue holds the name of the property on the view which holds the value
        we want to filter by.
        Example: the Item model has filterfield "category" and filtervalue "category" so
        we filter the queryset with {"category": self.category}
        """
        queryset = super().get_queryset()
        if hasattr(self.model, "filterfield") and hasattr(self.model, "filtervalue"):
            queryset = queryset.filter(
                **{self.model.filterfield: getattr(self, self.model.filtervalue)}
            )
        return queryset
