from django.contrib import admin
from . import models


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "last_login")


admin.site.register(models.User, UserAdmin)


class ActorAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user")


admin.site.register(models.Actor, ActorAdmin)
