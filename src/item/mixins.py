import logging
from eav.models import Attribute

from django.shortcuts import get_object_or_404

from category.mixins import CategoryViewMixin
from .models import Item

class ItemViewMixin(CategoryViewMixin):
    """
    The ItemViewMixin sets self.item based on item_slug from the URL
    """
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.item = get_object_or_404(
            Item,
            category=self.category,
            slug=self.kwargs["item_slug"],
        )

class ItemFormMixin(object):
    """
    Mixin with shared logic used by ItemCreateView and
    ItemUpdateView.
    """
    def get_form(self, form_class=None):
        """
        Get the form and loop over the fields.
        Fixup the dropdown for any object-type fields.
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
                if not a.extra_data:
                    continue
                field[1].queryset = Item.objects.filter(category_id=a.extra_data.split("=")[1])
        return form


