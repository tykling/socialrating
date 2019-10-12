from django.urls import path, include

app_name = "settings"

urlpatterns = [
    path("update/", TeamUpdateView.as_view(), name="update"),
    path("members/", TeamMemberView.as_view(), name="members"),
    path("categories/", include("category.urls", namespace="category")),
    path("contexts/", include("context.urls", namespace="context")),
]
