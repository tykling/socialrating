from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse

from team.mixins import TeamViewMixin, TeamAdminRequiredMixin

from .models import Context


class ContextListView(TeamViewMixin, ListView):
    model = Context
    paginate_by = 100
    template_name = 'context_list.html'


class ContextDetailView(TeamViewMixin, DetailView):
    model = Context
    template_name = 'context_detail.html'
    slug_url_kwarg = 'context_slug'


class ContextCreateView(TeamViewMixin, TeamAdminRequiredMixin, CreateView):
    model = Context
    template_name = 'context_form.html'
    fields = ['name', 'description']

    def form_valid(self, form):
        """
        Set the team
        """
        category = form.save(commit=False)
        category.team = self.team
        category.save()
        messages.success(self.request, "New context created!")

        return redirect(reverse('team:context:list', kwargs={'team_slug': self.team.slug}))


class ContextUpdateView(TeamViewMixin, TeamAdminRequiredMixin, CreateView):
    model = Context
    template_name = 'context_form.html'
    fields = ['name', 'description']


class ContextDeleteView(TeamViewMixin, TeamAdminRequiredMixin, DeleteView):
    model = Context
    template_name = 'context_delete.html'
    slug_url_kwarg = 'context_slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Context %s has been deleted, along with all Reviews, Votes, Tags and Content that related to it." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:context:list', kwargs={
            'team_slug': self.team.slug,
        }))

