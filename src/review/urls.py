from django.urls import path, include

from socialrating.generic_fk_urls import generic_fk_urls

from .views import (
    ReviewListView,
    ReviewCreateView,
    ReviewDetailView,
    ReviewSettingsView,
    ReviewUpdateView,
    ReviewDeleteView,
)

app_name = "review"

urlpatterns = [
    path("", ReviewListView.as_view(), name="list"),
    path("create/", ReviewCreateView.as_view(), name="create"),
    path(
        "<uuid:review_uuid>/",
        include(
            [
                path("", ReviewDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", ReviewSettingsView.as_view(), name="settings"),
                            path("update/", ReviewUpdateView.as_view(), name="update"),
                            path("delete/", ReviewDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
                path("votes/", include("vote.urls", namespace="vote")),
                path("", include(generic_fk_urls)),
            ]
        ),
    ),
]
