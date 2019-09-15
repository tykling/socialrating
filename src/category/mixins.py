import logging

from django.shortcuts import get_object_or_404

from team.mixins import TeamSlugMixin
from .models import Category

logger = logging.getLogger("socialrating.%s" % __name__)


class CategorySlugMixin(TeamSlugMixin):
    """
    The CategorySlugMixin sets self.category based on category_slug
    """
    def setup(self, *args, **kwargs):
        # call super() now so TeamSlugMixin runs first
        super().setup(*args, **kwargs)
        self.category = get_object_or_404(
            Category,
            team=self.team,
            slug=self.kwargs["category_slug"],
        )

    def get_context_data(self, **kwargs):
        """
        Add Category to context
        """
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

