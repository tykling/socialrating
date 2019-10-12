from django.urls import path, include

from .views import *

app_name = "attachment"

urlpatterns = [
    path("", AttachmentListView.as_view(), name="list"),
    path("create/", AttachmentCreateView.as_view(), name="create"),
    path(
        "<uuid:attachment_uuid>/",
        include(
            [
                path("", AttachmentDetailView.as_view(), name="detail"),
                path("file/", AttachmentFileView.as_view(), name="attachment"),
                path(
                    "settings/",
                    include(
                        [
                            path("", AttachmentDetailView.as_view(), name="settings"),
                            path(
                                "update/", AttachmentUpdateView.as_view(), name="update"
                            ),
                            path(
                                "delete/", AttachmentDeleteView.as_view(), name="delete"
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
