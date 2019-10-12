from django.urls import path, include
from django.views.generic import TemplateView

from category.views import CategoryListView
from context.views import ContextListView
from .views import *

app_name = "team"

urlpatterns = [
    path("", TeamListView.as_view(), name="list"),
    path("create/", TeamCreateView.as_view(), name="create"),
    path(
        "<slug:team_slug>/",
        include(
            [
                path("", TeamDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", TeamDetailView.as_view(), name="settings"),
                            path("update/", TeamUpdateView.as_view(), name="update"),
                            path("delete/", TeamDeleteView.as_view(), name="delete"),
                            path("members/", TeamMemberView.as_view(), name="members"),
                        ]
                    ),
                ),
                path("categories/", include("category.urls", namespace="category")),
                path("contexts/", include("context.urls", namespace="context")),
            ]
        ),
    ),
]
