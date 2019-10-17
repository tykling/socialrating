from django.urls import path, include

from .views import *

app_name = "vote"

urlpatterns = [
    path("", VoteListView.as_view(), name="list"),
    path("create/", VoteCreateView.as_view(), name="create"),
    path(
        "<uuid:vote_uuid>/",
        include(
            [
                path("", VoteDetailView.as_view(), name="detail"),
                path(
                    "settings/",
                    include(
                        [
                            path("", VoteSettingsView.as_view(), name="settings"),
                            path("update/", VoteUpdateView.as_view(), name="update"),
                            path("delete/", VoteDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
            ]
        ),
    ),
]
