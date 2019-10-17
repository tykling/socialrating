from django.urls import path, include

from .views import *

app_name = "rating"

urlpatterns = [
    path("", RatingListView.as_view(), name="list"),
    path("create/", RatingCreateView.as_view(), name="create"),
    path(
        "<slug:rating_slug>/",
        include(
            [
                path("", RatingDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", RatingSettingsView.as_view(), name="settings"),
                            path("update/", RatingUpdateView.as_view(), name="update"),
                            path("delete/", RatingDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
            ]
        ),
    ),
]
