from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse

from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Item
from .forms import ItemForm
from .mixins import ItemFormMixin


class ItemListView(SRListViewMixin, ListView):
    model = Item
    paginate_by = 100
    template_name = "item_list.html"
    permission_required = "item.view_item"


class ItemCreateView(SRViewMixin, ItemFormMixin, CreateView):
    """
    ItemCreateView uses ItemForm which subclasses
    eav.forms.BaseDynamicEntityForm so the required
    django-eav2 fields are added dynamically
    """

    model = Item
    template_name = "item_form.html"
    form_class = ItemForm
    permission_required = "category.add_item"

    def get_permission_object(self):
        """
        Only users with category.add_item permission for
        self.category are allowed to create new Items
        """
        return self.category

    def get_initial(self):
        """
        Set self.object to an empty Item with only category defined,
        this helps django-eav2 to know which Attributes to include in
        the dynamically generated form for the new Item.
        """
        self.object = Item(category=self.category)

    def form_valid(self, form):
        item = form.save()
        messages.success(self.request, "New Item created!")
        return redirect(
            reverse(
                "team:category:item:detail",
                kwargs={
                    "team_slug": self.team.slug,
                    "category_slug": self.category.slug,
                    "item_slug": item.slug,
                },
            )
        )


class ItemDetailView(SRViewMixin, DetailView):
    model = Item
    template_name = "item_detail.html"
    slug_url_kwarg = "item_slug"
    permission_required = "item.view_item"


class ItemSettingsView(SRViewMixin, DetailView):
    model = Item
    template_name = "item_settings.html"
    slug_url_kwarg = "item_slug"
    permission_required = "item.change_item"


class ItemUpdateView(SRViewMixin, ItemFormMixin, UpdateView):
    model = Item
    template_name = "item_form.html"
    form_class = ItemForm
    slug_url_kwarg = "item_slug"
    permission_required = "item.change_item"

    def form_valid(self, form):
        item = form.save()
        messages.success(self.request, "Item updated!")
        return redirect(item.get_absolute_url())


class ItemDeleteView(SRViewMixin, DeleteView):
    model = Item
    template_name = "item_delete.html"
    slug_url_kwarg = "item_slug"
    permission_required = "item.delete_item"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Item has been deleted, along with all Reviews and Votes that related to it.",
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "team:category:item:list",
            kwargs={"team_slug": self.team.slug, "category_slug": self.category.slug},
        )
