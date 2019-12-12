from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin

from .models import Thread


class ThreadAdmin(PermissionsAdminMixin, GuardedModelAdmin, admin.ModelAdmin):
    model = Thread

    list_display = ["uuid", "forum", "actor", "subject", "locked"]


admin.site.register(Thread, ThreadAdmin)
