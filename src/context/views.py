from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse

from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Context


class ContextListView(SRListViewMixin, ListView):
    model = Context
    paginate_by = 100
    template_name = "context_list.html"
    permission_required = "context.view_context"


class ContextCreateView(SRViewMixin, CreateView):
    model = Context
    template_name = "context_form.html"
    fields = ["name", "description"]
    permission_required = "team.add_context"

    def get_permission_object(self):
        """
        Only users with team.add_context permission for self.team are
        allowed to create new Contexts
        """
        return self.team

    def form_valid(self, form):
        """
        Set the team and save
        """
        context = form.save(commit=False)
        context.team = self.team
        context.save()
        messages.success(self.request, "New context created!")
        return redirect(context.get_absolute_url())


class ContextDetailView(SRViewMixin, DetailView):
    model = Context
    template_name = "context_detail.html"
    slug_url_kwarg = "context_slug"
    permission_required = "context.view_context"


class ContextSettingsView(SRViewMixin, DetailView):
    model = Context
    template_name = "context_settings.html"
    slug_url_kwarg = "context_slug"
    permission_required = "context.change_context"


class ContextUpdateView(SRViewMixin, UpdateView):
    model = Context
    template_name = "context_form.html"
    fields = ["name", "description"]
    slug_url_kwarg = "context_slug"
    permission_required = "context.change_context"

    def form_valid(self, form):
        context = form.save()
        messages.success(self.request, "Context updated!")
        return redirect(
            reverse(
                "team:context:detail",
                kwargs={"team_slug": self.team.slug, "context_slug": context.slug},
            )
        )


class ContextDeleteView(SRViewMixin, DeleteView):
    model = Context
    template_name = "context_delete.html"
    slug_url_kwarg = "context_slug"
    permission_required = "context.delete_context"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Context has been deleted, along with all Reviews, Votes, Tags and Content that related to it.",
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("team:context:list", kwargs={"team_slug": self.team.slug})
