from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin
from .models import Vote


class VoteAdmin(PermissionsAdminMixin, GuardedModelAdmin):
    pass


admin.site.register(Vote, VoteAdmin)
