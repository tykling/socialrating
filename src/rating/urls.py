from django.urls import path, include

from .views import *

app_name = 'rating'

urlpatterns = [
    path(
        'create/',
        RatingCreateView.as_view(),
        name='create',
    ),
    path(
        '<slug:rating_slug>/',
        include([
            path(
                '',
                RatingDetailView.as_view(),
                name='detail',
            ),
            path(
                'update/',
                RatingUpdateView.as_view(),
                name='update',
            ),
            path(
                'delete/',
                RatingDeleteView.as_view(),
                name='delete',
            ),
         ]),
    ),
]

