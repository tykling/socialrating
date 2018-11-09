from django.shortcuts import render

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.contenttypes.models import ContentType

from eav.models import Attribute

from team.mixins import TeamViewMixin
from category.mixins import CategoryViewMixin
from .models import Item
from .forms import ItemForm


class ItemListView(CategoryViewMixin, ListView):
    model = Item
    paginate_by = 100
    template_name = 'item_list.html'


class ItemDetailView(CategoryViewMixin, DetailView):
    model = Item
    template_name = 'item_detail.html'
    slug_url_kwarg = 'item_slug'


class ItemFormMixin(object):
    def get_form(self, form_class=None):
        """
        Get the form and loop over the fields
        """
        form = super().get_form(form_class)
        for field in form.fields.items():
            # see if we can find an EAV attribute matching this field
            try:
                a = Attribute.objects.get(slug=field[0])
            except Attribute.DoesNotExist:
                continue

            # does this EAV field have datatype 'Django Object'?
            if a.datatype != 'object':
                continue

            # filter this dropdown to show only the relevant Items
            if a.entity_ct and a.entity_id:
                field[1].queryset = Item.objects.filter(category_id=a.extra_data.split("=")[1])
        return form


class ItemCreateView(CategoryViewMixin, ItemFormMixin, CreateView):
    model = Item
    template_name = 'item_form.html'
    form_class = ItemForm

    def get_initial(self):
        """
        Set self.object to an empty Item with only category defined,
        so eav knows which Attributes to include in the form for this new Item.
        """
        self.object = Item(category=self.category)


class ItemUpdateView(CategoryViewMixin, ItemFormMixin, UpdateView):
    model = Item
    template_name = 'item_form.html'
    form_class = ItemForm
    slug_url_kwarg = 'item_slug'

