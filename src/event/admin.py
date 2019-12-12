from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin
from . import models


class EventAdmin(PermissionsAdminMixin, GuardedModelAdmin):
    list_display = [
        "uuid",
        "content_type",
        "object_id",
        "event_object",
        "event_type",
        "actor",
        "timestamp",
    ]
    list_filter = ["event_type", "content_type"]
    search_fields = (
        "uuid",
        "content_type",
        "object_id",
        "event_object",
        "event_type",
        "actor",
    )


admin.site.register(models.Event, EventAdmin)
