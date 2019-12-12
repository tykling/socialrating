from django.urls import path, include

from .views import EventListView, EventDetailView

app_name = "attachment"

urlpatterns = [
    path("", EventListView.as_view(), name="list"),
    path(
        "<uuid:event_uuid>/",
        include([path("", EventDetailView.as_view(), name="detail")]),
    ),
]
