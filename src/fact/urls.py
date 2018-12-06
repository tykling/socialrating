from django.urls import path, include

from .views import *

app_name = 'fact'

urlpatterns = [
    path(
        'create/',
        FactCreateView.as_view(),
        name='create',
    ),
    path(
        '<slug:fact_slug>/',
        include([
            path(
                '',
                FactDetailView.as_view(),
                name='detail',
            ),
            path(
                'update/',
                FactUpdateView.as_view(),
                name='update',
            ),
            path(
                'delete/',
                FactDeleteView.as_view(),
                name='delete',
            ),
        ]),
    ),
]

