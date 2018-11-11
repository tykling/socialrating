from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.contenttypes.models import ContentType
from django import forms

from eav.models import Attribute

from team.mixins import TeamViewMixin
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


class CategoryCreateView(TeamViewMixin, CreateView):
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


class CategoryUpdateView(TeamViewMixin, CreateView):
    model = Category
    template_name = 'category_form.html'
    fields = ['name', 'description']


class AttributeCreateView(CategoryViewMixin, CreateView):
    model = Attribute
    template_name = 'attribute_form.html'
    fields = ['name', 'datatype', 'description', 'required']

    def get_form(self, form_class=None):
        """
        Fixup a few things in the dynamically generated EAV form
        - Make help_text for the fields more userfriendly
        - add Category select (only relevant for datatype=Django Object fields)
        """
        form = super().get_form(form_class)
        form.fields['datatype'].help_text='The datatype for this Attribute.'

        # add Category field
        form.fields['category'] = forms.ModelChoiceField(
            queryset=self.team.categories.all(),
            help_text='The Category for this Object field',
        )

        return form

    def form_valid(self, form):
        """
        Set the entity_ct and entity_id based on self.category.
        Also set the slug for this attribute.
        Also set extra_data based on the Category picker in the form,
        but only if this Attribute is of type "Django Object"
        """
        attribute = form.save(commit=False)
        attribute.slug = self.category.create_attribute_slug(attribute.name)
        attribute.entity_ct=ContentType.objects.get(app_label='category', model='category')
        attribute.entity_id=self.category.id
        if attribute.datatype == 'object':
            attribute.extra_data = 'category.id=%s' % self.category.pk
        attribute.save()
        messages.success(self.request, "New attribute created!")

        return redirect(reverse('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
        }))


class AttributeUpdateView(CategoryViewMixin, UpdateView):
    model = Attribute
    template_name = 'attribute_form.html'
    slug_url_kwarg = 'attribute_slug'
    fields = ['name', 'description', 'required']

    def get_success_url(self):
        return reverse('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
        })

