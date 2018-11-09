import logging

from django.apps import AppConfig
from django.db.models.signals import post_save

logger = logging.getLogger("socialrating.%s" % __name__)


class ActorConfig(AppConfig):
    name = 'actor'

    def ready(self):
        """
        Connect signal to create an Actor every time a Django User object is created
        """
        logger.debug("Connecting User post_save signal to create Actor objects...")
        from .models import User
        from .signals import create_actor
        post_save.connect(create_actor, sender=User, dispatch_uid="create_actor")

