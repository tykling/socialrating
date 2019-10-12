import factory

from .models import Context


class ContextFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Context

    name = factory.Faker("sentence")
    description = factory.Faker("text")
