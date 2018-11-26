from django.urls import path, include

from .views import *

app_name = 'review'

urlpatterns = [
    path(
        'create/',
        ReviewCreateView.as_view(),
        name='create',
    ),
    path(
        '<uuid:review_uuid>/',
        include([
            path(
                '',
                ReviewDetailView.as_view(),
                name='detail',
            ),
            path(
                'update/',
                ReviewUpdateView.as_view(),
                name='update',
            ),
            path(
                'delete/',
                ReviewDeleteView.as_view(),
                name='delete',
            ),
         ]),
    ),
]

