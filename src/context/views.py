from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from guardian.mixins import PermissionListMixin

from team.mixins import *
from utils.mixins import PermissionRequiredOr403Mixin

from .models import Context


class ContextListView(TeamSlugMixin, PermissionListMixin, ListView):
    model = Context
    paginate_by = 100
    template_name = 'context_list.html'
    permission_required = 'context.view_context'

    def get_queryset(self):
        return super().get_queryset().filter(team=self.team)


class ContextDetailView(TeamSlugMixin, PermissionRequiredOr403Mixin, DetailView):
    model = Context
    template_name = 'context_detail.html'
    slug_url_kwarg = 'context_slug'
    permission_required = 'context.view_context'


class ContextCreateView(TeamSlugMixin, PermissionRequiredOr403Mixin, CreateView):
    model = Context
    template_name = 'context_form.html'
    fields = ['name', 'description']
    permission_required = 'team.change_team'

    def get_permission_object(self):
        """
        Only users with team.change_team permission for self.team are
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


class ContextUpdateView(TeamSlugMixin, PermissionRequiredOr403Mixin, UpdateView):
    model = Context
    template_name = 'context_form.html'
    fields = ['name', 'description']
    slug_url_kwarg = 'context_slug'
    permission_required = 'context.change_context'

    def form_valid(self, form):
        context = form.save()
        messages.success(self.request, "Context updated!")
        return redirect(reverse('team:context:detail', kwargs={
            'team_slug': self.team.slug,
            'context_slug': context.slug,
        }))


class ContextDeleteView(TeamSlugMixin, PermissionRequiredOr403Mixin, DeleteView):
    model = Context
    template_name = 'context_delete.html'
    slug_url_kwarg = 'context_slug'
    permission_required = 'context.delete_context'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Context has been deleted, along with all Reviews, Votes, Tags and Content that related to it.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:context:list', kwargs={
            'team_slug': self.team.slug,
        }))

