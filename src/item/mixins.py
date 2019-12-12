from fact.models import Fact
from item.models import Item


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
