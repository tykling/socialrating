import eav.registry

class CategoryEavConfig(eav.registry.EavConfig):
    @classmethod
    def get_attributes(cls, entity):
        """
        Return just the Facts / EAV attributes which apply to this Category
        """
        return entity.facts.all()

