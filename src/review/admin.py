from django.contrib import admin
from . import models


class ReviewAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Review, ReviewAdmin)
