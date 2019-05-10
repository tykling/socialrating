from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

from category.mixins import CategorySlugMixin
from .models import Item
from .forms import ItemForm
from .mixins import ItemFormMixin


class ItemListView(CategorySlugMixin, PermissionListMixin, ListView):
    model = Item
    paginate_by = 100
    template_name = 'item_list.html'
    permission_required = 'item.view_item'


class ItemDetailView(CategorySlugMixin, PermissionRequiredMixin, DetailView):
    model = Item
    template_name = 'item_detail.html'
    slug_url_kwarg = 'item_slug'
    permission_required = 'item.view_item'


class ItemCreateView(CategorySlugMixin, PermissionRequiredMixin, ItemFormMixin, CreateView):
    """
    ItemCreateView uses ItemForm which subclasses
    eav.forms.BaseDynamicEntityForm so the required
    django-eav2 fields are added dynamically
    """
    model = Item
    template_name = 'item_form.html'
    form_class = ItemForm

    def setup(self, *args, **kwargs):
        """
        TODO: Figure out why PermissionRequiredMixin doesn't seem to work with CreateView
        """
        super().setup(*args, **kwargs)
        if not self.request.user.has_perm('item.add_item'):
            raise Http404

    def get_initial(self):
        """
        Set self.object to an empty Item with only category defined,
        this helps django-eav2 to know which Attributes to include in
        the dynamically generated form for the new Item.
        """
        self.object = Item(category=self.category)

    def get_form(self):
        form = super().get_form()
        # include the category in help_text for the name field
        form.fields['name'].help_text = 'The name of this %s' % self.category.name

        # include the category in the label for all fields
        for name, field in form.fields.items():
            field.label="%s %s" % (self.category.name, field.label)
        return form


class ItemUpdateView(CategorySlugMixin, PermissionRequiredMixin, ItemFormMixin, UpdateView):
    model = Item
    template_name = 'item_form.html'
    form_class = ItemForm
    slug_url_kwarg = 'item_slug'
    permission_required = 'item.change_item'


class ItemDeleteView(CategorySlugMixin, PermissionRequiredMixin, DeleteView):
    model = Item
    template_name = 'item_delete.html'
    slug_url_kwarg = 'item_slug'
    permission_required = 'item.delete_item'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Item %s has been deleted, along with all Reviews and Votes that related to it." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:detail', kwargs={
            'team_slug': self.team.slug,
        }))

