from django.urls import path, include

from .views import *

app_name = 'context'

urlpatterns = [
    path(
        '',
        ContextListView.as_view(),
        name='list',
    ),
    path(
        'create/',
        ContextCreateView.as_view(),
        name='create',
    ),
    path(
        '<slug:context_slug>/',
        include([
            path(
                '',
                ContextDetailView.as_view(),
                name='detail',
            ),
            path(
                'update/',
                ContextUpdateView.as_view(),
                name='update',
            ),
            path(
                'delete/',
                ContextDeleteView.as_view(),
                name='delete',
            ),
         ]),
    ),
]

