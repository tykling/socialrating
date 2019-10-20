from django.contrib import admin
from django.contrib.auth import views as authviews
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
import allauth.account.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/signup/",
        allauth.account.views.signup,
        name="account_signup",
        kwargs={"breadcrumb_title": "Sign Up"},
    ),
    path(
        "accounts/login/",
        allauth.account.views.login,
        name="account_login",
        kwargs={"breadcrumb_title": "Sign In"},
    ),
    path("accounts/", include("allauth.urls")),
    path("", TemplateView.as_view(template_name="frontpage.html"), name="frontpage"),
    path("teams/", include("team.urls", namespace="team")),
]
