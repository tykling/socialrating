import logging

from eav.models import Attribute
from django.shortcuts import get_object_or_404, reverse
from django.contrib.contenttypes.models import ContentType

from category.mixins import CategorySlugMixin
from .models import Item

logger = logging.getLogger("socialrating.%s" % __name__)


class ItemSlugMixin(CategorySlugMixin):
    """
    The ItemSlugMixin sets self.item based on item_slug from the URL,
    checks permission to view the item and also sets breadcrumbs.
    Inherits from CategoryMixin so we also have self.category available
    """

    def setup(self, *args, **kwargs):
        # call super() now so CategorySlugMixin runs first
        super().setup(*args, **kwargs)
        self.item = get_object_or_404(
            Item, category=self.category, slug=self.kwargs["item_slug"]
        )

        # check permissions
        if not self.request.user.has_perm("item.view_item", self.item):
            raise PermissionDenied

        # add breadcrumb for item list
        self.breadcrumbs.append(
            (
                Item.breadcrumb_list_name,
                reverse(
                    "team:category:item:list",
                    kwargs={
                        "team_slug": self.team.slug,
                        "category_slug": self.category.slug,
                    },
                ),
            )
        )
        # add breadcrumb for this item
        self.breadcrumbs.append((self.item.name, self.item.get_absolute_url()))

        # only if this mixin is the leftmost
        if self.__class__.__mro__[1].__module__ == "item.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Item to context
        """
        context = super().get_context_data(**kwargs)
        context["item"] = self.item
        return context


class ItemFormMixin:
    """
    Mixin with shared logic used by ItemCreateView and ItemUpdateView.
    """

    def get_form(self, form_class=None):
        """
        Get the form and loop over the fields.
        Fixup the dropdown for any object-type fields.
        """
        form = super().get_form(form_class)
        for field in form.fields.items():
            # see if we can find an EAV object attribute matching this field
            try:
                a = Attribute.objects.get(
                    # the field name is the slug
                    slug=field[0],
                    # the content type id is for Category (because that is where we define Facts)
                    entity_ct_id=ContentType.objects.get(
                        app_label="category", model="category"
                    ).id,
                    # and the entity_id is the current items categorys id
                    entity_id=self.category.id,
                    # and the datatype should be object, we dont care about the rest
                    datatype="object",
                )
            except Attribute.DoesNotExist:
                # this is not an EAV field, or not type object, nothing to do here
                continue

            # filter the dropdown to show only the relevant Items
            field[1].queryset = Item.objects.filter(
                category_id=a.extra_data["category_id"]
            )

        # we're done fixing all fields, return the form
        return form
