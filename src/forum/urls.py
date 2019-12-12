from django.urls import path, include

from .views import (
    ForumListView,
    ForumCreateView,
    ForumDetailView,
    ForumSettingsView,
    ForumUpdateView,
    ForumDeleteView,
)

app_name = "forum"

urlpatterns = [
    path("", ForumListView.as_view(), name="list"),
    path("create/", ForumCreateView.as_view(), name="create"),
    path(
        "<slug:forum_slug>/",
        include(
            [
                path("", ForumDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", ForumSettingsView.as_view(), name="settings"),
                            path("update/", ForumUpdateView.as_view(), name="update"),
                            path("delete/", ForumDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
                path("threads/", include("thread.urls", namespace="thread")),
            ]
        ),
    ),
]
