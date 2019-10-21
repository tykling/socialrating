from django.contrib import admin
from eav.forms import BaseDynamicEntityForm
from eav.admin import BaseEntityAdmin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin
from .models import Item


class ItemAdminForm(BaseDynamicEntityForm):
    model = Item


class ItemAdmin(PermissionsAdminMixin, GuardedModelAdmin, BaseEntityAdmin):
    form = ItemAdminForm


admin.site.register(Item, ItemAdmin)
