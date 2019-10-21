from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin
from .models import Rating


class RatingAdmin(PermissionsAdminMixin, GuardedModelAdmin):
    pass


admin.site.register(Rating, RatingAdmin)
