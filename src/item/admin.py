from django.contrib import admin
from eav.forms import BaseDynamicEntityForm
from eav.admin import BaseEntityAdmin

from .models import Item


class ItemAdminForm(BaseDynamicEntityForm):
    model = Item


class ItemAdmin(BaseEntityAdmin):
    form = ItemAdminForm

admin.site.register(Item, ItemAdmin)

