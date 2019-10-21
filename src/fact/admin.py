from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin
from .models import Fact


class FactAdmin(PermissionsAdminMixin, GuardedModelAdmin):
    pass


admin.site.register(Fact, FactAdmin)
