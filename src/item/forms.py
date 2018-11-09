from eav.forms import BaseDynamicEntityForm

from .models import Item


class ItemForm(BaseDynamicEntityForm):
    class Meta:
        model = Item
        fields = ['name']

