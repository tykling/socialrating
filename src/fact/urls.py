from django.urls import path, include

from .views import (
    FactListView,
    FactCreateView,
    FactDetailView,
    FactSettingsView,
    FactUpdateView,
    FactDeleteView,
)

app_name = "fact"

urlpatterns = [
    path("", FactListView.as_view(), name="list"),
    path("create/", FactCreateView.as_view(), name="create"),
    path(
        "<slug:fact_slug>/",
        include(
            [
                path("", FactDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", FactSettingsView.as_view(), name="settings"),
                            path("update/", FactUpdateView.as_view(), name="update"),
                            path("delete/", FactDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
            ]
        ),
    ),
]
