import logging

from django.shortcuts import get_object_or_404, reverse

from review.mixins import ReviewMixin
from .models import Attachment

logger = logging.getLogger("socialrating.%s" % __name__)


class AttachmentMixin(ReviewMixin):
    """
    The AttachmentSlugMixin sets self.attachment based on attachment_uuid from the URL,
    also checks permissions and sets breadcrumbs.
    Inherits from ReviewSlugMixin so we have self.review available
    """

    def setup(self, *args, **kwargs):
        # call super() now so ReviewSlugMixin runs first
        super().setup(*args, **kwargs)

        # get the attachment
        self.attachment = get_object_or_404(
            Attachment, review=self.review, uuid=self.kwargs["attachment_uuid"]
        )

        # check permissions
        if not self.request.user.has_perm(
            "attachment.view_attachment", self.attachment
        ):
            raise PermissionDenied

        # add breadcrumb for attachment list
        self.breadcrumbs.append(
            (
                Attachment.breadcrumb_list_name,
                reverse(
                    "team:category:item:review:attachment:list",
                    kwargs={
                        "team_slug": self.team.slug,
                        "category_slug": self.category.slug,
                        "item_slug": self.item.slug,
                        "review_uuid": self.review.uuid,
                    },
                ),
            )
        )

        # add breadcrumb for this attachment
        self.breadcrumbs.append(
            (self.attachment.uuid, self.attachment.get_absolute_url())
        )

        # only if this mixin is the leftmost
        if self.__class__.__mro__[1].__module__ == "attachment.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Attachment to context
        """
        context = super().get_context_data(**kwargs)
        context["attachment"] = self.attachment
        return context
