import logging

from django.shortcuts import get_object_or_404, reverse

from review.mixins import ReviewSlugMixin
from .models import Vote

logger = logging.getLogger("socialrating.%s" % __name__)


class VoteSlugMixin(ReviewSlugMixin):
    """
    The VoteSlugMixin sets self.vote based on vote_uuid from the URL,
    also checks permissions and sets breadcrumbs.
    Inherits from ReviewSlugMixin so we have self.review available
    """

    def setup(self, *args, **kwargs):
        # call super() now so ReviewSlugMixin runs first
        super().setup(*args, **kwargs)

        # get the vote
        self.vote = get_object_or_404(
            Vote, review=self.review, uuid=self.kwargs["vote_uuid"]
        )

        # check permissions
        if not self.request.user.has_perm("vote.view_vote", self.vote):
            raise PermissionDenied

        # add breadcrumb for vote list
        self.breadcrumbs.append(
            (
                Vote.breadcrumb_list_name,
                reverse(
                    "team:category:item:review:vote:list",
                    kwargs={
                        "team_slug": self.team.slug,
                        "category_slug": self.category.slug,
                        "item_slug": self.item.slug,
                        "review_uuid": self.review.uuid,
                    },
                ),
            )
        )

        # add breadcrumb for this vote
        self.breadcrumbs.append((self.vote.uuid, self.vote.get_absolute_url()))

        # only if this mixin is the leftmost
        if self.__class__.__mro__[1].__module__ == "vote.mixins":
            # if this is a CreateView add a link to the ListView first
            if self.request.resolver_match.url_name == "create":
                self.add_listview_breadcrumb()
            # add action breadcrumb
            self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Vote to context
        """
        context = super().get_context_data(**kwargs)
        context["vote"] = self.vote
        return context
