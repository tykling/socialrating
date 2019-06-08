import logging

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.contenttypes.models import ContentType

from guardian.mixins import PermissionListMixin
from utils.mixins import PermissionRequiredOr403Mixin

from .models import Team, Membership
from .mixins import *

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamListView(LoginRequiredMixin, PermissionListMixin, ListView):
    """
    The TeamListView requires no special permissions.
    It simply lists the teams which the current user has permissions to see.
    """
    model = Team
    paginate_by = 100
    template_name = 'team_list.html'
    permission_required = 'team.view_team'


class TeamCreateView(LoginRequiredMixin, CreateView):
    """
    The TeamCreateView requires no special permissions.
    """
    model = Team
    template_name = 'team_form.html'
    fields = ['name', 'description']

    def form_valid(self, form):
        """
        Set the current user as team founder and as an admin member of the new team
        """
        # save team including founder
        team = form.save(commit=False)
        team.founder = self.request.user.actor
        team.save()

        # add founder as team member
        membership = Membership.objects.create(
            actor=self.request.user.actor,
            team=team,
            admin=True
        )
        messages.success(self.request, "New team created!")

        return redirect(reverse('team:detail', kwargs={'team_slug': team.slug}))


class TeamDetailView(PermissionRequiredOr403Mixin, DetailView):
    model = Team
    template_name = 'team_detail.html'
    slug_url_kwarg = 'team_slug'
    permission_required = 'team.view_team'


class TeamMemberView(PermissionRequiredOr403Mixin, DetailView):
    model = Team
    template_name = 'team_members.html'
    slug_url_kwarg = 'team_slug'
    permission_required = 'team.view_team'


class TeamUpdateView(PermissionRequiredOr403Mixin, UpdateView):
    model = Team
    template_name = 'team_form.html'
    fields = ['description']
    slug_url_kwarg = 'team_slug'
    permission_required = 'team.change_team'

    def form_valid(self, form):
        team = form.save()
        messages.success(self.request, "Team updated!")
        return redirect(reverse('team:detail', kwargs={'team_slug': team.slug}))

