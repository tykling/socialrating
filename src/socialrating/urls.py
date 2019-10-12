from django.contrib import admin
from django.contrib.auth import views as authviews
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", TemplateView.as_view(template_name="frontpage.html"), name="frontpage"),
    path("teams/", include("team.urls", namespace="team")),
]
