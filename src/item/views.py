from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType

from category.mixins import CategoryViewMixin
from team.mixins import TeamAdminRequiredMixin
from .models import Item
from .forms import ItemForm
from .mixins import ItemFormMixin


class ItemListView(CategoryViewMixin, ListView):
    model = Item
    paginate_by = 100
    template_name = 'item_list.html'


class ItemCreateView(CategoryViewMixin, ItemFormMixin, CreateView):
    model = Item
    template_name = 'item_form.html'
    form_class = ItemForm

    def get_initial(self):
        """
        Set self.object to an empty Item with only category defined,
        this helps django-eav2 to know which Attributes to include in
        the dynamically generated form for the new Item.
        """
        self.object = Item(category=self.category)


class ItemDetailView(CategoryViewMixin, DetailView):
    model = Item
    template_name = 'item_detail.html'
    slug_url_kwarg = 'item_slug'


class ItemUpdateView(CategoryViewMixin, ItemFormMixin, UpdateView):
    model = Item
    template_name = 'item_form.html'
    form_class = ItemForm
    slug_url_kwarg = 'item_slug'


class ItemDeleteView(CategoryViewMixin, TeamAdminRequiredMixin, DeleteView):
    model = Item
    template_name = 'item_delete.html'
    slug_url_kwarg = 'item_slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Item %s has been deleted, along with all Reviews and Votes that related to it." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:category:detail', kwargs={
            'camp_slug': self.camp.slug,
            'category_slug': self.category.slug,
        }))

