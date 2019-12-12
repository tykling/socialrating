import logging

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from guardian.mixins import PermissionListMixin

from utils.mixins import SRViewMixin

from .models import Thread

logger = logging.getLogger("socialrating.%s" % __name__)


class ThreadListView(SRViewMixin, PermissionListMixin, ListView):
    model = Thread
    paginate_by = 100
    template_name = "thread_list.html"
    permission_required = "thread.view_thread"


class ThreadCreateView(SRViewMixin, CreateView):
    model = Thread
    template_name = "thread_form.html"
    fields = ["subject", "locked"]
    permission_required = "forum.add_thread"

    def get_permission_object(self):
        """
        Only users with forum.add_thread permission for self.forum are
        allowed to create new Threads
        """
        return self.forum

    def form_valid(self, form):
        """
        Set the forum before saving
        """
        thread = form.save(commit=False)
        thread.forum = self.forum
        thread.actor = self.request.user.actor
        thread.save()
        messages.success(self.request, "New thread created!")
        return redirect(
            reverse(
                "team:thread:detail",
                kwargs={
                    "team_slug": self.team.slug,
                    "forum_slug": self.forum.slug,
                    "thread_slug": thread.slug,
                },
            )
        )


class ThreadDetailView(SRViewMixin, DetailView):
    model = Thread
    slug_url_kwarg = "thread_slug"
    permission_required = "thread.view_thread"
    template_name = "thread_detail.html"


class ThreadSettingsView(SRViewMixin, DetailView):
    model = Thread
    slug_url_kwarg = "thread_slug"
    permission_required = "forum.change_thread"
    template_name = "thread_settings.html"


class ThreadUpdateView(SRViewMixin, UpdateView):
    model = Thread
    template_name = "thread_form.html"
    fields = ["locked"]
    slug_url_kwarg = "thread_slug"
    permission_required = "forum.change_thread"

    def form_valid(self, form):
        messages.success(self.request, "Thread updated!")
        return redirect(
            reverse(
                "team:forum:thread:settings",
                kwargs={
                    "team_slug": self.team.slug,
                    "forum_slug": self.forum.slug,
                    "thread_slug": self.thread.slug,
                },
            )
        )


class ThreadDeleteView(SRViewMixin, DeleteView):
    model = Thread
    template_name = "thread_delete.html"
    slug_url_kwarg = "thread_slug"
    permission_required = "forum.delete_thread"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Thread has been deleted, along with all Comments in it, and their related content.",
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "team:forum:thread:list",
            kwargs={"team_slug": self.team.slug, "forum_slug": self.forum.slug},
        )
