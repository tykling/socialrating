import logging

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import Http404
from django.core.exceptions import PermissionDenied
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

from team.mixins import *
from utils.mixins import PermissionRequiredOr403Mixin
from utils.mixins import BreadCrumbMixin as BCMixin
from .models import Category
from .mixins import CategorySlugMixin

logger = logging.getLogger("socialrating.%s" % __name__)


class CategoryListView(TeamSlugMixin, PermissionListMixin, BCMixin, ListView):
    model = Category
    paginate_by = 100
    template_name = "category_list.html"
    permission_required = "category.view_category"

    def get_queryset(self):
        return super().get_queryset().filter(team=self.team)


class CategoryCreateView(
    TeamSlugMixin, PermissionRequiredOr403Mixin, BCMixin, CreateView
):
    model = Category
    template_name = "category_form.html"
    fields = ["name", "description"]
    permission_required = "team.add_category"

    def get_permission_object(self):
        """
        Only users with team.add_category permission for self.team are
        allowed to create new Categories
        """
        return self.team

    def form_valid(self, form):
        """
        Set the team before saving
        """
        category = form.save(commit=False)
        category.team = self.team
        category.save()
        messages.success(self.request, "New category created!")
        return redirect(
            reverse(
                "team:category:detail",
                kwargs={"team_slug": self.team.slug, "category_slug": category.slug},
            )
        )


class CategoryDetailView(
    CategorySlugMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView
):
    model = Category
    template_name = "category_detail.html"
    slug_url_kwarg = "category_slug"
    permission_required = "category.view_category"


class CategoryUpdateView(
    CategorySlugMixin, PermissionRequiredOr403Mixin, BCMixin, UpdateView
):
    model = Category
    template_name = "category_form.html"
    fields = ["name", "description"]
    slug_url_kwarg = "category_slug"
    permission_required = "category.change_category"

    def form_valid(self, form):
        """
        Because of the way django-eav2 validates fields we have to do
        a bit of extra work here.
        The problem is that any EAV fields on this category which are
        required=True will prevent saving changes to the 'name' and
        'description' fields of this Category.
        So we temporarily set required to False for all the EAV fields
        for the category, save, and then set required back True.
        """
        # get all attributes
        attributes = self.get_object().eav.get_all_attributes()
        required_eav_ids = []

        # loop over the required ones and set required=False
        for eav in attributes.filter(required=True):
            required_eav_ids.append(eav.pk)
            eav.required = False
            eav.save()

        # save the category
        category = form.save()

        # set required to True again
        category.eav.get_all_attributes().filter(id__in=required_eav_ids).update(
            required=True
        )

        # all done
        messages.success(self.request, "Category updated!")
        return redirect(
            reverse(
                "team:category:detail",
                kwargs={"team_slug": self.team.slug, "category_slug": category.slug},
            )
        )


class CategoryDeleteView(
    CategorySlugMixin, PermissionRequiredOr403Mixin, BCMixin, DeleteView
):
    model = Category
    template_name = "category_delete.html"
    slug_url_kwarg = "category_slug"
    permission_required = "category.delete_category"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Category has been deleted, along with all Items belonging to it, and their related content.",
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("team:category:list", kwargs={"team_slug": self.team.slug})
