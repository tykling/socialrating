import logging

from guardian.mixins import PermissionRequiredMixin
import django.views.generic
from django.shortcuts import reverse

logger = logging.getLogger("socialrating.%s" % __name__)


class PermissionRequiredOr403Mixin(PermissionRequiredMixin):
    """
    A subclass of PermissionRequireMixin with the properties we want
    to use in SocialRating views
    """

    accept_global_perms = True
    return_403 = True


class BreadCrumbMixin:
    @property
    def breadcrumb_title(self):
        if isinstance(self, django.views.generic.list.ListView):
            # default to the breadcrumb list name from the model
            return self.model.breadcrumb_list_name
        elif isinstance(self, django.views.generic.edit.CreateView):
            # return a default string for all CreateViews
            return "Create"
        elif isinstance(self, django.views.generic.edit.UpdateView):
            # return a default string for all UpdateViews
            return "Update"
        elif isinstance(self, django.views.generic.edit.DeleteView):
            # return a default string for all DeleteViews
            return "Delete"
        else:
            # DetailViews will get the breadcrumb from their respective mixins
            return

    def add_listview_breadcrumb(self):
        """
        Return a breadcrumb for the view named "list" in the same
        namespace as the current resolver match, with the same kwargs.
        Used to get a link to the matching ListView for a CreateView
        """
        self.breadcrumbs.append(
            (
                self.model.breadcrumb_list_name,
                reverse(
                    viewname=":".join(self.request.resolver_match.namespaces) + ":list",
                    kwargs=self.request.resolver_match.kwargs,
                ),
            )
        )

    def add_action_breadcrumb(self):
        """
        Return a breadcrumb for the current views action, like "Create" or "Delete"
        Override the defaults set in BreadCrumbMixin by setting breadcrumb_title on the view.
        """
        # add self.breadcrumb_title too (if we have one)
        if hasattr(self, "breadcrumb_title") and self.breadcrumb_title:
            self.breadcrumbs.append((self.breadcrumb_title, self.request.path))
