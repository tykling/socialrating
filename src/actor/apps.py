import logging

from django.apps import AppConfig

logger = logging.getLogger("socialrating.%s" % __name__)


class ActorConfig(AppConfig):
    name = "actor"
