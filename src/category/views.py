from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import Http404
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

from team.mixins import *
from .models import Category


class CategoryListView(TeamSlugMixin, PermissionListMixin, ListView):
    model = Category
    paginate_by = 100
    template_name = 'category_list.html'
    permission_required = 'category.view_category'


class CategoryDetailView(TeamSlugMixin, PermissionRequiredMixin, DetailView):
    model = Category
    template_name = 'category_detail.html'
    slug_url_kwarg = 'category_slug'
    permission_required = 'category.view_category'


class CategoryCreateView(TeamSlugMixin, CreateView):
    model = Category
    template_name = 'category_form.html'
    fields = ['name', 'description']

    def setup(self, *args, **kwargs):
        """
        TODO: Figure out why PermissionRequiredMixin doesn't seem to work with CreateView
        """
        super().setup(*args, **kwargs)
        if not self.request.user.has_perm('category.add_category'):
            raise Http404

    def form_valid(self, form):
        """
        Set the team before saving
        """
        category = form.save(commit=False)
        category.team = self.team
        category.save()
        messages.success(self.request, "New category created!")
        return redirect(reverse('team:category:list', kwargs={
            'team_slug': self.team.slug
        }))


class CategoryUpdateView(TeamSlugMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    template_name = 'category_form.html'
    fields = ['name', 'description']
    slug_url_kwarg = 'category_slug'
    permission_required = 'category.change_category'

    def form_valid(self, form):
        """
        Because of the way django-eav2 validates fields we have to fall back to raw sql here.

        The problem is that any EAV fields on this category which are required=True will
        prevent saving changes to the 'name' and 'description' fields of this Category.

        An alternative solution without raw sql might be to temporarily set required to False
        for all the EAV fields for the category, save, and then set required back to what it was,
        all inside a transaction.
        """
        # get category from database
        category = self.get_object()
        # get DB connection cursor
        cursor = connection.cursor()
        # update the DB entry
        cursor.execute('UPDATE category_category SET name=%s, description=%s WHERE id=%s', [
            form.cleaned_data['name'],
            form.cleaned_data['description'],
            category.id
        ])
        # done
        messages.success(self.request, "Category updated!")
        return redirect(reverse('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': category.slug,
        }))


class CategoryDeleteView(TeamSlugMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_delete.html'
    slug_url_kwarg = 'category_slug'
    permission_required = 'category.delete_category'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Category %s has been deleted, along with all Items belonging to it, and their related content." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:category:list', kwargs={
            'team_slug': self.team.slug,
        }))

