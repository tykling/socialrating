from django.urls import path, include

from .views import *

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
                            path("", ItemDetailView.as_view(), name="settings"),
                            path("update/", ItemUpdateView.as_view(), name="update"),
                            path("delete/", ItemDeleteView.as_view(), name="delete"),
                        ]
                    ),
                ),
                path("reviews/", include("review.urls", namespace="review")),
            ]
        ),
    ),
]
