from django.contrib import admin


class PermissionsAdminMixin:
    """
    A mixin to add an admin action to run the grant_permissions() method on
    a model instance. Useful when developing and changing permissions code, should
    never be needed under normal circumstances.
    """

    actions = ["grant_permissions"]

    def grant_permissions(self, request, queryset):
        for category in queryset:
            category.grant_permissions()
