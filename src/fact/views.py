from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.contenttypes.models import ContentType
from django import forms
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

# from eav.models import Attribute as Fact
from fact.models import Fact

from category.mixins import CategorySlugMixin
from utils.mixins import BreadCrumbMixin as BCMixin
from utils.mixins import PermissionRequiredOr403Mixin

from .mixins import FactSlugMixin


class FactListView(CategorySlugMixin, PermissionListMixin, BCMixin, ListView):
    """
    Facts are just another name for django-eav2 attributes,
    so we use the eav.models.Attribute model.
    """

    model = Fact
    template_name = "fact_list.html"
    permission_required = "fact.view_fact"
    breadcrumb_title = "Facts"


class FactCreateView(
    CategorySlugMixin, PermissionRequiredOr403Mixin, BCMixin, CreateView
):
    """
    Facts are just another name for django-eav2 attributes,
    so we use the eav.models.Attribute model.
    """

    model = Fact
    template_name = "fact_form.html"
    fields = ["name", "datatype", "description", "required"]
    permission_required = "category.add_fact"

    def get_permission_object(self):
        """
        Only users with category.add_fact permission for self.category are
        allowed to create new Facts
        """
        return self.category

    def get_form(self, form_class=None):
        """
        Fixup a few things in the dynamically generated EAV form
        - Make help_text for the fields more userfriendly
        - add Category select (only relevant for datatype=Django Object fields)
        """
        form = super().get_form(form_class)
        form.fields["name"].help_text = "The name of this Fact."
        form.fields["datatype"].help_text = "The datatype for this Fact."

        # add Category field
        form.fields["category"] = forms.ModelChoiceField(
            queryset=self.team.categories.all(),
            help_text="The Category of the Object. Only relevant if this is an Object field",
            required=False,
        )

        return form

    def form_valid(self, form):
        """
        Set the entity_ct and entity_id based on self.category.
        Also set the slug for this Fact.
        Also set extra_data based on the Category picker in the form,
        but only if this Fact is of type "Django Object"
        """
        fact = form.save(commit=False)
        fact.slug = self.category.create_fact_slug(fact_name=fact.name)
        fact.entity_ct = ContentType.objects.get(app_label="category", model="category")
        fact.entity_id = self.category.id
        if fact.datatype == "object":
            fact.extra_data = {"category_id": form.cleaned_data["category"].pk}
        fact.save()
        messages.success(self.request, "New Fact created!")

        return redirect(
            reverse(
                "team:category:detail",
                kwargs={
                    "team_slug": self.team.slug,
                    "category_slug": self.category.slug,
                },
            )
        )


class FactDetailView(FactSlugMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView):
    """
    Facts are just another name for django-eav2 attributes,
    so we use the eav.models.Attribute model.
    """

    model = Fact
    template_name = "fact_detail.html"
    slug_url_kwarg = "fact_slug"
    permission_required = "fact.view_fact"


class FactUpdateView(FactSlugMixin, PermissionRequiredOr403Mixin, BCMixin, UpdateView):
    """
    Facts are just another name for django-eav2 attributes,
    so we use the eav.models.Attribute model.
    """

    model = Fact
    template_name = "fact_form.html"
    slug_url_kwarg = "fact_slug"
    permission_required = "fact.change_fact"
    fields = ["name", "description", "required"]

    def get_success_url(self):
        return reverse(
            "team:category:detail",
            kwargs={"team_slug": self.team.slug, "category_slug": self.category.slug},
        )


class FactDeleteView(FactSlugMixin, PermissionRequiredOr403Mixin, BCMixin, DeleteView):
    """
    Facts are just another name for django-eav2 attributes,
    so we use the eav.models.Attribute model.
    """

    model = Fact
    template_name = "fact_delete.html"
    slug_url_kwarg = "fact_slug"
    permission_required = "fact.delete_fact"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["category"] = self.category
        return context

    def delete(self, request, *args, **kwargs):
        # first delete all values for this Fact
        self.get_object().value_set.all().delete()
        # add a message for the user
        messages.success(
            self.request,
            "Fact %s has been deleted, along with all data related to it."
            % self.get_object(),
        )
        # and delete the Fact itself
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "team:category:detail",
            kwargs={"team_slug": self.team.slug, "category_slug": self.category.slug},
        )
