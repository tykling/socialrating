import logging

from django.shortcuts import get_object_or_404, reverse

from team.mixins import TeamSlugMixin
from .models import Context

logger = logging.getLogger("socialrating.%s" % __name__)


class ContextSlugMixin(TeamSlugMixin):
    """
    The ContextSlugMixin sets self.context based on context_slug,
    and adds breadcrumbs
    """

    def setup(self, *args, **kwargs):
        # call super() now so TeamSlugMixin runs first
        super().setup(*args, **kwargs)
        self.context = get_object_or_404(
            Context, team=self.team, slug=self.kwargs["context_slug"]
        )

        # check permissions
        if not self.request.user.has_perm("context.view_context", self.context):
            raise PermissionDenied

        # add breadcrumb for context list
        self.breadcrumbs.append(
            (
                Context.breadcrumb_list_name,
                reverse("team:context:list", kwargs={"team_slug": self.team.slug}),
            )
        )

        # add breadcrumb for this context
        self.breadcrumbs.append((self.context.name, self.context.get_absolute_url()))

        # only if this mixin is the leftmost, add self.breadcrumb_title too (if we have one)
        if self.__class__.__mro__[1].__module__ == "context.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Context to template context
        """
        context = super().get_context_data(**kwargs)
        context["context"] = self.context
        return context
