from django.urls import path, include

from .views import (
    ContextListView,
    ContextCreateView,
    ContextDetailView,
    ContextSettingsView,
    ContextUpdateView,
    ContextDeleteView,
)

app_name = "context"

urlpatterns = [
    path("", ContextListView.as_view(), name="list"),
    path("create/", ContextCreateView.as_view(), name="create"),
    path(
        "<slug:context_slug>/",
        include(
            [
                path("", ContextDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", ContextSettingsView.as_view(), name="settings"),
                            path("update/", ContextUpdateView.as_view(), name="update"),
                            path("delete/", ContextDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
            ]
        ),
    ),
]
