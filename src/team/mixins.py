import logging

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin

from team.models import Team

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamMemberRequiredMixin(LoginRequiredMixin):
    """
    A mixin to sets self.team from URL kwarg team_slug, and return 404 if request.user is not a team member
    """
    def setup(self, *args, **kwargs):
        self.team = get_object_or_404(Team, slug=self.kwargs["team_slug"])
        if not self.team.members.filter(user=self.request.user).exists():
            logger.error("The current user %s is not a member of the team %s" % (self.request.user, self.team))
            raise Http404


class TeamAdminRequiredMixin(TeamMemberRequiredMixin):
    """
    A mixin to check if the current user is an admin the current team
    """
    def setup(self, *args, **kwargs):
        if self.request.user.actor not in self.team.members.filter(admin=True):
            logger.error("The current user %s is not an admin of the team %s" % (self.request.user, self.team))
            messages.error(self.request, "You must be an admin of the Team to perform this action")
            raise Http404


class TeamViewMixin(TeamMemberRequiredMixin):
    """
    This mixin filters get_queryset to only show items related to self.team. This
    requires the models used in views that use TeamViewMixin to have a team_filter property,
    a string (or list of strings) like "category__team" to be used in .filter()
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
            if hasattr(self, 'pk_url_kwarg'):
                pk = self.kwargs.get(self.pk_url_kwarg)
                if pk is not None:
                    # We should also filter for the pk of the object
                    filter_dict['pk'] = pk

            # get slug from kwargs if we have it
            if hasattr(self, 'slug_url_kwarg'):
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

