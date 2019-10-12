import logging

from django.apps import AppConfig
from django.db.models.signals import post_save

logger = logging.getLogger("socialrating.%s" % __name__)


class FactConfig(AppConfig):
    name = "fact"

    def ready(self):
        """
        Connect signal to create permissions for Facts (which is another name for django-eav2 Attributes)
        """
        logger.debug(
            "Connecting Attribute post_save signal to create permissions for Facts..."
        )
        from eav.models import Attribute
        from .signals import create_fact_permissions

        post_save.connect(
            create_fact_permissions,
            sender=Attribute,
            dispatch_uid="create_fact_permissions",
        )
