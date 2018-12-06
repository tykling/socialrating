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

from .models import Team, Membership
from .mixins import TeamMemberRequiredMixin
from eventlog.models import Event

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
        return Team.objects.filter(memberships__actor=self.request.user.actor).distinct()


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
    template_name = 'team_form.html'
    fields = ['name', 'description']

    def form_valid(self, form):
        """
        Set the current user as an admin member of the new team
        """
        # save team including founder
        team = form.save(commit=False)
        team.founder = self.request.user.actor
        team.save()
        # register event
        #Event.objects.create(
        #    event_type=Event.CREATE,
        #    content_type=ContentType.objects.get_for_model(Team),
        #    object_id=team.pk,
        #)

        # add founder as team member
        membership = Membership.objects.create(
            actor=self.request.user.actor,
            team=team,
            admin=True
        )
        messages.success(self.request, "New team created!")

        return redirect(reverse('team:list'))


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    template_name = 'team_form.html'
    fields = ['description']

