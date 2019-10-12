import factory

from .models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("sentence")
    description = factory.Faker("text")
