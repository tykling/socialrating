from eav.models import Attribute


class Fact(Attribute):
    """
    Fact is just another name for eav Attributes.
    We use this proxy model instead of using Attributes directly.
    """

    class Meta:
        proxy = True

    breadcrumb_list_name = "Facts"
