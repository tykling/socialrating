from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.contenttypes.models import ContentType
from django import forms

from eav.models import Attribute, Value

from category.mixins import CategorySlugMixin


class FactCreateView(CategorySlugMixin, CreateView):
    """
    Facts are just another name for django-eav2 attributes,
    so we use the eav.models.Attribute model.
    """
    model = Attribute
    template_name = 'fact_form.html'
    fields = ['name', 'datatype', 'description', 'required']

    def get_form(self, form_class=None):
        """
        Fixup a few things in the dynamically generated EAV form
        - Make help_text for the fields more userfriendly
        - add Category select (only relevant for datatype=Django Object fields)
        """
        form = super().get_form(form_class)
        form.fields['name'].help_text='The name of this Fact.'
        form.fields['datatype'].help_text='The datatype for this Fact.'

        # add Category field
        form.fields['category'] = forms.ModelChoiceField(
            queryset=self.team.categories.all(),
            help_text='The Category of the Object. Only relevant if this is an Object field',
            required=False,
        )

        return form

    def form_valid(self, form):
        """
        Set the entity_ct and entity_id based on self.category.
        Also set the slug for this Fact.
        Also set extra_data based on the Category picker in the form,
        but only if this Fact is of type "Django Object"
        """
        fact = form.save(commit=False)
        fact.slug = self.category.create_fact_slug(fact_name=fact.name)
        fact.entity_ct=ContentType.objects.get(app_label='category', model='category')
        fact.entity_id=self.category.id
        if fact.datatype == 'object':
            fact.extra_data = 'category.id=%s' % form.cleaned_data['category'].pk
        fact.save()
        messages.success(self.request, "New Fact created!")

        return redirect(reverse('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
        }))


class FactDetailView(CategorySlugMixin, DetailView):
    model = Attribute
    template_name = 'fact_detail.html'
    slug_url_kwarg = 'fact_slug'


class FactUpdateView(CategorySlugMixin, UpdateView):
    """
    Facts are just another name for django-eav2 attributes,
    so we use the eav.models.Attribute model.
    """
    model = Attribute
    template_name = 'fact_form.html'
    slug_url_kwarg = 'fact_slug'
    fields = ['name', 'description', 'required']

    def get_success_url(self):
        return reverse('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
        })


class FactDeleteView(CategorySlugMixin, DeleteView):
    model = Attribute
    template_name = 'fact_delete.html'
    slug_url_kwarg = 'fact_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['category'] = self.category
        return context

    def delete(self, request, *args, **kwargs):
        Value.objects.filter(attribute=self.get_object()).delete()
        messages.success(self.request, "Fact %s has been deleted, along with all data related to it." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
        }))

