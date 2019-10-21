import logging

from django.shortcuts import get_object_or_404, reverse
from django.core.exceptions import PermissionDenied
from guardian.core import ObjectPermissionChecker

from category.mixins import CategoryMixin
from fact.models import Fact
from .models import Item

logger = logging.getLogger("socialrating.%s" % __name__)


class ItemMixin(CategoryMixin):
    """
    The ItemMixin sets self.item based on item_slug from the URL,
    checks permission to view the item and also sets breadcrumbs.
    Inherits from CategoryMixin so we also have self.category available
    """

    def setup(self, *args, **kwargs):
        # call super() now so CategoryMixin runs first
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
        context["item_perms"] = ObjectPermissionChecker(self.request.user).get_perms(
            self.item
        )
        return context


class ItemFormMixin:
    """
    Mixin with shared logic used by ItemCreateView and ItemUpdateView.
    """

    def get_form(self, form_class=None):
        """
        Get the form and loop over the fields.
        Fixup the object dropdown for any object-type fields.
        Fix the help_text a few places.
        """
        form = super().get_form(form_class)
        for field in form.fields.items():
            # see if we can find an EAV object attribute matching this form field
            try:
                fact = Fact.objects.get(
                    # the field name is the fact slug
                    slug=field[0],
                    # and category is the current one
                    category=self.category,
                    # and the datatype is 'object', we dont care about the rest
                    datatype="object",
                )
            except Fact.DoesNotExist:
                # this is not an EAV field, or not type object, nothing to do here
                continue

            # filter the dropdown to show only the relevant Items
            field[1].queryset = Item.objects.filter(category=fact.object_category)

        # include the category in help_text for the name field
        form.fields["name"].help_text = "The name of this %s" % self.category.name

        # include the category in the label for all fields
        for name, field in form.fields.items():
            field.label = "%s %s" % (self.category.name, field.label)
        return form

        # we're done fixing all fields, return the form
        return form
