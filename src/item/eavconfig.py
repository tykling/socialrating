import eav.registry


class ItemEavConfig(eav.registry.EavConfig):
    @classmethod
    def get_attributes(cls, entity):
        """
        Items have no Facts / EAV attributes directly, so we return the
        Facts which apply to the Category of this Item.
        """
        return entity.category.facts.all()
