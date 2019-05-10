import logging

from django.shortcuts import get_object_or_404

from item.mixins import ItemSlugMixin
from .models import Review

logger = logging.getLogger("socialrating.%s" % __name__)


class ReviewSlugMixin(ItemSlugMixin):
    """
    The ReviewSlugMixin sets self.review based on review_uuid from the URL
    Inherits from ItemSlugMixin so we also have self.item available
    """
    def setup(self, *args, **kwargs):
        logger.debug("Inside ReviewSlugMixin")
        # call super() now so ItemSlugMixin runs first
        super().setup(*args, **kwargs)
        self.review = get_object_or_404(
            Review,
            item=self.item,
            uuid=self.kwargs["review_uuid"],
        )

