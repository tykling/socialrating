from django.urls import path, include

from .views import *

app_name = 'category'

urlpatterns = [
    path(
        '',
        CategoryListView.as_view(),
        name='list',
    ),
    path(
        'create/',
        CategoryCreateView.as_view(),
        name='create',
    ),
    path(
        '<slug:category_slug>/',
        include([
            path(
                '',
                CategoryDetailView.as_view(),
                name='detail',
            ),
            path('items/',
                include('item.urls', namespace='item')
            ),
            path(
                'attributes/',
                include([
                    path(
                        'create/',
                        AttributeCreateView.as_view(),
                        name='attribute_create',
                    ),
                    path(
                        '<slug:attribute_slug>/',
                        AttributeUpdateView.as_view(),
                        name='attribute_update',
                    ),
                ]),
            ),
         ]),
    ),
]

