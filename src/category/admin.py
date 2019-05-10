from django.contrib import admin
from eav.forms import BaseDynamicEntityForm
from eav.admin import BaseEntityAdmin
from guardian.admin import GuardedModelAdmin

from .models import Category


class CategoryAdminForm(BaseDynamicEntityForm):
    model = Category


class CategoryAdmin(GuardedModelAdmin, BaseEntityAdmin):
    form = CategoryAdminForm

admin.site.register(Category, CategoryAdmin)

