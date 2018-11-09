import logging

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse

from .models import Team, Membership
from .mixins import TeamMemberRequiredMixin

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamListView(LoginRequiredMixin, ListView):
    """
    The TeamListView requires no special permissions. It simply lists the teams of which the current user is a member.
    """
    model = Team
    paginate_by = 100
    template_name = 'team_list.html'

    def get_queryset(self):
        """
        Only list Teams which the current user is a member of
        """
        return Team.objects.filter(members__membership__actor__user=self.request.user).distinct()


class TeamDetailView(TeamMemberRequiredMixin, DetailView):
    model = Team
    template_name = 'team_detail.html'
    slug_url_kwarg = 'team_slug'


class TeamMemberView(TeamMemberRequiredMixin, DetailView):
    model = Team
    template_name = 'team_members.html'
    slug_url_kwarg = 'team_slug'


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'team_create.html'
    fields = ['name']

    def form_valid(self, form):
        """
        Set the current user as an admin member of the new team
        """
        logger.debug("debug her")
        team = form.save(commit=False)
        team.founder = self.request.user.actor
        team.save()
        Membership.objects.create(
            actor=self.request.user.actor,
            team=team,
            admin=True
        )
        messages.error(self.request, "New team created!")

        return redirect(reverse('team:list',))

