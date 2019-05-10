from django.contrib import admin
from . import models
from guardian.admin import GuardedModelAdmin

class TeamAdmin(GuardedModelAdmin):
    pass

class MembershipAdmin(GuardedModelAdmin):
    def get_username(self, obj):
        return obj.actor.user.username

    def get_name(self, obj):
        return obj.actor.user.full_name

    def get_email(self, obj):
        return obj.actor.user.email

    def get_uuid(self, obj):
        return obj.actor.uuid

    list_display = ['get_uuid', 'get_username', 'get_name', 'get_email', 'team', 'admin']
    list_filter = ['team', 'admin', 'actor']
    search_fields = ('actor__uuid', 'actor__user__username', 'actor__user__email', 'actor__user__first_name', 'actor__user__last_name')


admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Membership, MembershipAdmin)
