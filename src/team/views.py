import logging

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse

from guardian.mixins import PermissionListMixin
from utils.mixins import PermissionRequiredOr403Mixin
from utils.mixins import BreadCrumbMixin as BCMixin

from .models import Team
from .mixins import TeamMixin

logger = logging.getLogger("socialrating.%s" % __name__)


class TeamListView(LoginRequiredMixin, PermissionListMixin, ListView):
    """
    The TeamListView requires no special permissions.
    It simply lists the teams which the current user has permissions to see.
    """

    model = Team
    paginate_by = 100
    template_name = "team_list.html"
    permission_required = "team.view_team"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        # the TeamListView has no mixin to set breadcrumbs so we set it manually
        self.breadcrumbs = [(self.model.breadcrumb_list_name, self.request.path)]


class TeamCreateView(LoginRequiredMixin, BCMixin, CreateView):
    """
    The TeamCreateView requires no special permissions.
    """

    model = Team
    template_name = "team_form.html"
    fields = ["name", "description"]

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        # the TeamCreateView has no mixin to set breadcrumbs so we set it manually
        self.breadcrumbs = [(self.model.breadcrumb_list_name, reverse("team:list"))]
        self.breadcrumbs.append((self.breadcrumb_title, self.request.path))

    def form_valid(self, form):
        """
        Set the current user as team founder of the new team
        """
        # save team including founder
        team = form.save(commit=False)
        team.founder = self.request.user.actor
        team.save()

        messages.success(self.request, "New team created!")
        return redirect(reverse("team:detail", kwargs={"team_slug": team.slug}))


class TeamDetailView(TeamMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView):
    model = Team
    slug_url_kwarg = "team_slug"
    permission_required = "team.view_team"
    template_name = "team_detail.html"

    def get_context_data(self, **kwargs):
        """
        Add Team to context
        """
        context = super().get_context_data(**kwargs)
        context["team"] = self.team
        if self.team.reviews.exists():
            context["review"] = self.team.reviews.latest("created")
        if self.team.items.exists():
            context["item"] = self.team.items.latest("created")
        return context


class TeamSettingsView(TeamMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView):
    model = Team
    slug_url_kwarg = "team_slug"
    permission_required = "team.change_team"
    template_name = "team_settings.html"


class TeamMemberView(TeamMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView):
    model = Team
    template_name = "team_members.html"
    slug_url_kwarg = "team_slug"
    permission_required = "team.view_team"
    breadcrumb_title = "Members"


class TeamUpdateView(TeamMixin, PermissionRequiredOr403Mixin, BCMixin, UpdateView):
    model = Team
    template_name = "team_form.html"
    fields = ["description"]
    slug_url_kwarg = "team_slug"
    permission_required = "team.change_team"

    def form_valid(self, form):
        team = form.save()
        messages.success(self.request, "Team updated!")
        return redirect(reverse("team:detail", kwargs={"team_slug": team.slug}))


class TeamDeleteView(TeamMixin, PermissionRequiredOr403Mixin, BCMixin, DeleteView):
    model = Team
    template_name = "team_delete.html"
    slug_url_kwarg = "team_slug"
    permission_required = "team.delete_team"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Team has been deleted, along with all Contexts and Categories and Items belonging to it, and their related content.",
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("team:list")
