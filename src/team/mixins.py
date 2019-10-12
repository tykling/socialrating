import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from team.models import Team

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamSlugMixin:
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
        return context


class TeamFilterMixin:
    """
    This mixin filters get_queryset to only show items related to 
    self.team. This requires the models used in views that use TeamFilterMixin
    to have a team_filter property, a string (or list of strings) like 
    "category__team" to be used in .filter()
    """

    def get_queryset(self):
        """
        Filter queryset so it only includes objects related to the current team
        """
        queryset = super().get_queryset()

        # if this queryset is empty return it right away, because nothing for us to do
        if not queryset:
            return queryset

        # get the team_filter from the model
        team_filter = self.model.get_team_filter()

        # team_filter can be a string or a list of strings
        if isinstance(team_filter, str):
            team_filter = [team_filter]

        # loop over team_filters and return the first result we get
        for _filter in team_filter:
            # add team to the filter_dict
            filter_dict = {_filter: self.team}

            # get pk from kwargs if we have it
            if hasattr(self, "pk_url_kwarg"):
                pk = self.kwargs.get(self.pk_url_kwarg)
                if pk is not None:
                    # We should also filter for the pk of the object
                    filter_dict["pk"] = pk

            # get slug from kwargs if we have it
            if hasattr(self, "slug_url_kwarg"):
                slug = self.kwargs.get(self.slug_url_kwarg)
                if slug is not None and (pk is None or self.query_pk_and_slug):
                    # we should also filter for the slug of the object
                    filter_dict[self.get_slug_field()] = slug

            # do the filtering and return the result
            result = queryset.filter(**filter_dict)
            if result.exists():
                # we got some results with this team_filter, return now
                return result

        # no team_filter returned any results, return an empty queryset
        return result
