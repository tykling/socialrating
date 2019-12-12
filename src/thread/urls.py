from django.urls import path, include

from socialrating.generic_fk_urls import generic_fk_urls

from .views import (
    ThreadListView,
    ThreadCreateView,
    ThreadDetailView,
    ThreadSettingsView,
    ThreadUpdateView,
    ThreadDeleteView,
)

app_name = "thread"

urlpatterns = [
    path("", ThreadListView.as_view(), name="list"),
    path("create/", ThreadCreateView.as_view(), name="create"),
    path(
        "<slug:thread_slug>/",
        include(
            [
                path("", ThreadDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", ThreadSettingsView.as_view(), name="settings"),
                            path("update/", ThreadUpdateView.as_view(), name="update"),
                            path("delete/", ThreadDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
            ]
            + generic_fk_urls
        ),
    ),
]
