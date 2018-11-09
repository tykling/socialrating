import logging

from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger("socialrating.%s" % __name__)


def create_attributes(sender, instance, created, **kwargs):
    """
    When creating a new Item add all the Attributes from the Category
    """
    if not created:
        return

    logger.info("Creating Attributes for new Item %s" % instance.name)

    # get ContentType for Item objects
    ct = ContentType.objects.get(app_label="item", model="item")

    # loop over attributes and add them for this Item
    for attribute in instance.category.eav.get_all_attributes():
        logger.debug("Found category attribute %s" % attribute)
        attribute.pk = None
        attribute.entity_ct=ct
        attribute.entity_id=instance.pk
        attribute.slug=instance.create_attribute_slug(attribute.name)
        attribute.save()

    logger.info("Done creating Attributes for new Item %s" % instance.name)

