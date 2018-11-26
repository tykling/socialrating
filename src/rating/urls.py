from django.urls import path, include

from .views import *

app_name = 'rating'

urlpatterns = [
    path(
        'create/',
        RatingCreateView.as_view(),
        name='rating_create',
    ),
    path(
        '<slug:rating_slug>/',
        include([
            path(
                '',
                RatingDetailView.as_view(),
                name='rating_detail',
            ),
            path(
                'update/',
                RatingUpdateView.as_view(),
                name='rating_update',
            ),
            path(
                'delete/',
                RatingDeleteView.as_view(),
                name='rating_delete',
            ),
         ]),
    ),
]

