from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, reverse
from django.contrib import messages
from guardian.mixins import PermissionListMixin

from category.mixins import CategoryMixin
from utils.mixins import PermissionRequiredOr403Mixin
from utils.mixins import BreadCrumbMixin as BCMixin

from .models import Rating
from .mixins import RatingMixin


class RatingListView(CategoryMixin, PermissionListMixin, BCMixin, ListView):
    model = Rating
    paginate_by = 100
    template_name = "rating_list.html"
    permission_required = "rating.view_rating"

    def get_queryset(self):
        """
        Only return Ratings which belong to the current Category
        """
        return super().get_queryset().filter(category=self.category)


class RatingCreateView(
    CategoryMixin, PermissionRequiredOr403Mixin, BCMixin, CreateView
):
    model = Rating
    template_name = "rating_form.html"
    fields = ["name", "description", "max_rating", "icon"]
    permission_required = "category.add_rating"

    def get_permission_object(self):
        """
        Only users with category.add_rating permission for
        self.category are allowed to create new Ratings
        """
        return self.category

    def form_valid(self, form):
        """
        Set the category
        """
        rating = form.save(commit=False)
        rating.category = self.category
        rating.save()
        messages.success(self.request, "New rating created!")
        return redirect(
            reverse(
                "team:category:detail",
                kwargs={
                    "team_slug": self.team.slug,
                    "category_slug": self.category.slug,
                },
            )
        )


class RatingDetailView(RatingMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView):
    model = Rating
    template_name = "rating_detail.html"
    slug_url_kwarg = "rating_slug"
    permission_required = "rating.view_rating"


class RatingSettingsView(
    RatingMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView
):
    model = Rating
    template_name = "rating_settings.html"
    slug_url_kwarg = "rating_slug"
    permission_required = "rating.change_rating"


class RatingUpdateView(RatingMixin, PermissionRequiredOr403Mixin, BCMixin, UpdateView):
    model = Rating
    template_name = "rating_form.html"
    slug_url_kwarg = "rating_slug"
    permission_required = "rating.change_rating"
    fields = ["name", "description", "icon"]


class RatingDeleteView(RatingMixin, PermissionRequiredOr403Mixin, BCMixin, DeleteView):
    model = Rating
    template_name = "rating_delete.html"
    slug_url_kwarg = "rating_slug"
    permission_required = "rating.delete_rating"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Rating %s has been deleted, along with all Votes that related to it."
            % self.get_object(),
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "team:category:detail",
            kwargs={"team_slug": self.team.slug, "category_slug": self.category.slug},
        )
