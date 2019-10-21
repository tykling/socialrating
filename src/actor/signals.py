import logging

from guardian.conf import settings

from .models import Actor

logger = logging.getLogger("socialrating.%s" % __name__)


def create_actor(sender, instance, created, **kwargs):
    """
    Create a matching Actor object for this User object
    """
    if not created:
        # only create actor for new users
        return

    if instance.username == settings.ANONYMOUS_USER_NAME:
        # this is the django-guardian anonymous user,
        # no actor needed
        return

    # bail out if we already have an actor
    if hasattr(instance, "actor") and instance.actor:
        logger.error(
            "we already have an Actor for this User object, might be a duplicate signal?"
        )
        return

    # create Actor object
    Actor.objects.create(user=instance)
    # logger.debug("Created Actor %s for new User %s" % (actor.pk, instance.username))
