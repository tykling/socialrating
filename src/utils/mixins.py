from guardian.mixins import PermissionRequiredMixin

class PermissionRequiredOr403Mixin(PermissionRequiredMixin):
    """
    A subclass of PermissionRequireMixin with the properties we want
    to use in SocialRating views
    """
    accept_global_perms = True
    return_403 = True

