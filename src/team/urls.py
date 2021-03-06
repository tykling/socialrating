from django.urls import path, include

from .views import (
    TeamListView,
    TeamCreateView,
    TeamDetailView,
    TeamSettingsView,
    TeamUpdateView,
    TeamDeleteView,
    TeamMemberView,
)

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
                            path("", TeamSettingsView.as_view(), name="settings"),
                            path("update/", TeamUpdateView.as_view(), name="update"),
                            path("delete/", TeamDeleteView.as_view(), name="delete"),
                            path("members/", TeamMemberView.as_view(), name="members"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
                path("categories/", include("category.urls", namespace="category")),
                path("contexts/", include("context.urls", namespace="context")),
                path("forums/", include("forum.urls", namespace="forum")),
            ]
        ),
    ),
]
