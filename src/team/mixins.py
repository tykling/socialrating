import logging

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from team.models import Team

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamSlugMixin:
    """
    A mixin to set self.team based on team_slug from the URL
    It also checks if the current user is a member of the team and returns 404 if not.
    This check is mostly for the sake of the user. Proper permissions are checked later with guardian.
    """
    def setup(self, *args, **kwargs):
        logger.debug("Inside TeamSlugMixin")
        super().setup(*args, **kwargs)
        self.team = get_object_or_404(Team, slug=kwargs["team_slug"])
        if not hasattr(self.request.user, 'actor') or self.request.user.actor not in self.team.members.all():
            raise Http404


class TeamAdminRequiredMixin:
    """
    Check if self.request.user is an admin of self.team
    """
    def setup(self, *args, **kwargs):
        # run super() first so we have self.request available
        super().setup(*args, **kwargs)
        if self.request.user.actor not in self.team.members.filter(admin=True):
            raise Http404


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

