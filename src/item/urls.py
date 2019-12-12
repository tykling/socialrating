from django.urls import path, include

from socialrating.generic_fk_urls import generic_fk_urls

from .views import (
    ItemListView,
    ItemCreateView,
    ItemDetailView,
    ItemSettingsView,
    ItemUpdateView,
    ItemDeleteView,
)

app_name = "item"

urlpatterns = [
    path("", ItemListView.as_view(), name="list"),
    path("create/", ItemCreateView.as_view(), name="create"),
    path(
        "<slug:item_slug>/",
        include(
            [
                path("", ItemDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", ItemSettingsView.as_view(), name="settings"),
                            path("update/", ItemUpdateView.as_view(), name="update"),
                            path("delete/", ItemDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
                path("reviews/", include("review.urls", namespace="review")),
            ]
            + generic_fk_urls
        ),
    ),
]
