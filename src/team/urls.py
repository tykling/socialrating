from django.urls import path, include
from django.views.generic import TemplateView

from .views import *

app_name = 'team'

urlpatterns = [
    path(
        '',
        TeamListView.as_view(),
        name='list'
    ),

    path(
        'create/',
        TeamCreateView.as_view(),
        name='create'
    ),

    path(
        '<slug:team_slug>/',
        include([
            path(
                '',
                TeamDetailView.as_view(),
                name='detail',
            ),

            path(
                'members/',
                TeamMemberView.as_view(),
                name='members',
            ),

            path('categories/',
                include('category.urls', namespace='category')
            ),

        ]),
    ),
]

