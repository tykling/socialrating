import logging

from django.apps import AppConfig
from django.db.models.signals import post_save

logger = logging.getLogger("socialrating.%s" % __name__)


class ItemConfig(AppConfig):
    name = 'item'

    def ready(self):
        """
        Connect signal to create attributes for Items
        """
        #logger.debug("Connecting Item post_save signal to create Attributes...")
        from .models import Item
        from .signals import create_attributes
        #post_save.connect(create_attributes, sender=Item, dispatch_uid="create_attributes")

