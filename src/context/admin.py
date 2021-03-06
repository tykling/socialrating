from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin
from .models import Context


class ContextAdmin(PermissionsAdminMixin, GuardedModelAdmin):
    pass


admin.site.register(Context, ContextAdmin)
