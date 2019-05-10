import logging

from guardian.shortcuts import get_perms, assign_perm

logger = logging.getLogger("socialrating.%s" % __name__)


def create_fact_permissions(sender, instance, created, **kwargs):
    """
    Create permissions for Facts (Attributes) when created
    """
    if not created:
        # only create permissions for new Facts
        return
    category = instance.entity_fk

    # fix attribute.view_attribute permission if needed 
    if not 'attribute.view_attribute' in get_perms(category.team.group, instance):
        assign_perm('attribute.view_attribute', category.team.group, instance)

    # fix attribute.add_attribute permission if needed 
    if not 'attribute.add_attribute' in get_perms(category.team.admingroup, instance):
        assign_perm('attribute.add_attribute', category.team.group, instance)

    # fix attribute.change_attribute permission if needed 
    if not 'attribute.change_attribute' in get_perms(category.team.admingroup, instance):
        assign_perm('attribute.change_attribute', category.team.group, instance)

    # fix attribute.delete_attribute permission if needed 
    if not 'attribute.delete_attribute' in get_perms(category.team.admingroup, instance):
        assign_perm('attribute.delete_attribute', category.team.group, instance)

    logger.debug("Created permissions for Fact %s" % instance)

