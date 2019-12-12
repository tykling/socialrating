from django.urls import path, include

from .views import (
    CommentListView,
    CommentCreateView,
    CommentDetailView,
    CommentSettingsView,
    CommentUpdateView,
    CommentDeleteView,
)

app_name = "comment"

urlpatterns = [
    path("", CommentListView.as_view(), name="list"),
    path("create/", CommentCreateView.as_view(), name="create"),
    path(
        "<uuid:comment_uuid>/",
        include(
            [
                path("", CommentDetailView.as_view(), name="detail"),
                path("reply/", CommentCreateView.as_view(), name="reply"),
                path(
                    "settings/",
                    include(
                        [
                            path("", CommentSettingsView.as_view(), name="settings"),
                            path("update/", CommentUpdateView.as_view(), name="update"),
                            path("delete/", CommentDeleteView.as_view(), name="delete"),
                        ]
                    ),
                    kwargs={"settings_view": True},
                ),
                path(
                    "attachments/", include("attachment.urls", namespace="attachment")
                ),
                path("events/", include("event.urls", namespace="event")),
            ]
        ),
    ),
]
