from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

from team.mixins import *

from .models import Context


class ContextListView(TeamSlugMixin, PermissionListMixin, ListView):
    model = Context
    paginate_by = 100
    template_name = 'context_list.html'
    permission_required = 'context.view_context'


class ContextDetailView(TeamSlugMixin, PermissionRequiredMixin, DetailView):
    model = Context
    template_name = 'context_detail.html'
    slug_url_kwarg = 'context_slug'
    permission_required = 'context.view_context'


class ContextCreateView(TeamSlugMixin, CreateView):
    model = Context
    template_name = 'context_form.html'
    fields = ['name', 'description']

    def setup(self, *args, **kwargs):
        """
        TODO: Figure out why PermissionRequiredMixin doesn't seem to work with CreateView
        """
        super().setup(*args, **kwargs)
        if not self.request.user.has_perm('context.add_context'):
            raise Http404

    def form_valid(self, form):
        """
        Set the team
        """
        category = form.save(commit=False)
        category.team = self.team
        category.save()
        messages.success(self.request, "New context created!")
        return redirect(reverse('team:context:list', kwargs={'team_slug': self.team.slug}))


class ContextUpdateView(TeamSlugMixin, PermissionRequiredMixin, UpdateView):
    model = Context
    template_name = 'context_form.html'
    fields = ['name', 'description']
    permission_required = 'context.change_context'


class ContextDeleteView(TeamSlugMixin, PermissionRequiredMixin, DeleteView):
    model = Context
    template_name = 'context_delete.html'
    slug_url_kwarg = 'context_slug'
    permission_required = 'context.delete_context'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Context %s has been deleted, along with all Reviews, Votes, Tags and Content that related to it." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:context:list', kwargs={
            'team_slug': self.team.slug,
        }))

