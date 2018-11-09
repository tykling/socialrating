from django.contrib import admin
from eav.forms import BaseDynamicEntityForm
from eav.admin import BaseEntityAdmin

from .models import Category


class CategoryAdminForm(BaseDynamicEntityForm):
    model = Category


class CategoryAdmin(BaseEntityAdmin):
    form = CategoryAdminForm

admin.site.register(Category, CategoryAdmin)

