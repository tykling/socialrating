import logging

from .models import Actor

logger = logging.getLogger("socialrating.%s" % __name__)


def create_actor(sender, instance, created, **kwargs):
    """
    Create a matching Actor object for this User object
    """
    if not created:
        # only create actor for new users
        return

    # bail out if we already have an actor
    if hasattr(instance, 'actor'):
        logger.error("we already have an Actor for this User object, might be a duplicate signal?")
        return

    # create Actor object and return
    actor = Actor.objects.create(user=instance)
    logger.info("Created Actor %s for new User %s" % (actor.uuid, instance.username))

