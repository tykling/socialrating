import logging

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.shortcuts import redirect, reverse

from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Forum

logger = logging.getLogger("socialrating.%s" % __name__)


class ForumListView(SRListViewMixin, ListView):
    model = Forum
    paginate_by = 100
    template_name = "forum_list.html"
    permission_required = "forum.view_forum"


class ForumCreateView(SRViewMixin, CreateView):
    model = Forum
    template_name = "forum_form.html"
    fields = ["name", "description", "allow_new_threads"]
    permission_required = "team.add_forum"

    def get_permission_object(self):
        """
        Only users with team.add_forum permission for self.team are
        allowed to create new Categories
        """
        return self.team

    def form_valid(self, form):
        """
        Set the team before saving
        """
        forum = form.save(commit=False)
        forum.team = self.team
        forum.save()
        messages.success(self.request, "New forum created!")
        return redirect(
            reverse(
                "team:forum:detail",
                kwargs={"team_slug": self.team.slug, "forum_slug": forum.slug},
            )
        )


class ForumDetailView(SRViewMixin, DetailView):
    model = Forum
    slug_url_kwarg = "forum_slug"
    permission_required = "forum.view_forum"
    template_name = "forum_detail.html"


class ForumSettingsView(SRViewMixin, DetailView):
    model = Forum
    slug_url_kwarg = "forum_slug"
    permission_required = "forum.change_forum"
    template_name = "forum_settings.html"


class ForumUpdateView(SRViewMixin, UpdateView):
    model = Forum
    template_name = "forum_form.html"
    fields = ["name", "description", "allow_new_threads"]
    slug_url_kwarg = "forum_slug"
    permission_required = "forum.change_forum"

    def form_valid(self, form):
        messages.success(self.request, "Forum updated!")
        return redirect(
            reverse(
                "team:forum:settings",
                kwargs={
                    "team_slug": self.team.slug,
                    "forum_slug": self.get_object().slug,
                },
            )
        )


class ForumDeleteView(SRViewMixin, DeleteView):
    model = Forum
    template_name = "forum_delete.html"
    slug_url_kwarg = "forum_slug"
    permission_required = "forum.delete_forum"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Forum has been deleted, along with all Threads and Comments in it, and their related content.",
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("team:forum:list", kwargs={"team_slug": self.team.slug})
