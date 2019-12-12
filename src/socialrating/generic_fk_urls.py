from django.urls import path, include

generic_fk_urls = [
    path("attachments/", include("attachment.urls", namespace="attachment")),
    path("events/", include("event.urls", namespace="event")),
    path("comments/", include("comment.urls", namespace="comment")),
]
