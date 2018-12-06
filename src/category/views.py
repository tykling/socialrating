from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.contenttypes.models import ContentType

from team.mixins import TeamViewMixin, TeamAdminRequiredMixin
from .models import Category
from .mixins import CategoryViewMixin


class CategoryListView(TeamViewMixin, ListView):
    model = Category
    paginate_by = 100
    template_name = 'category_list.html'


class CategoryDetailView(TeamViewMixin, DetailView):
    model = Category
    template_name = 'category_detail.html'
    slug_url_kwarg = 'category_slug'


class CategoryCreateView(TeamViewMixin, TeamAdminRequiredMixin, CreateView):
    model = Category
    template_name = 'category_form.html'
    fields = ['name', 'description']

    def form_valid(self, form):
        """
        Set the team
        """
        category = form.save(commit=False)
        category.team = self.team
        category.save()
        messages.success(self.request, "New category created!")

        return redirect(reverse('team:category:list', kwargs={'team_slug': self.team.slug}))


class CategoryUpdateView(TeamViewMixin, TeamAdminRequiredMixin, CreateView):
    model = Category
    template_name = 'category_form.html'
    fields = ['name', 'description']

