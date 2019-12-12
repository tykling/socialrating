from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin

from .models import Forum


class ForumAdmin(PermissionsAdminMixin, GuardedModelAdmin, admin.ModelAdmin):
    model = Forum

    list_display = ["name", "team", "description", "allow_new_threads"]


admin.site.register(Forum, ForumAdmin)
