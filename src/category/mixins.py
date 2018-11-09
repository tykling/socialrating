import logging

from django.shortcuts import get_object_or_404

from team.mixins import TeamMemberRequiredMixin
from .models import Category

logger = logging.getLogger("socialrating.%s" % __name__)


class CategoryViewMixin(TeamMemberRequiredMixin):
    """
    The CategoryViewMixin sets self.category based on category_slug
    """
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.category = get_object_or_404(
            Category,
            team=self.team,
            slug=self.kwargs["category_slug"],
        )

