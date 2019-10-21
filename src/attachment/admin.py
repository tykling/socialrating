from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from utils.admin import PermissionsAdminMixin
from .models import Attachment


class AttachmentAdmin(PermissionsAdminMixin, GuardedModelAdmin):
    pass


admin.site.register(Attachment, AttachmentAdmin)
