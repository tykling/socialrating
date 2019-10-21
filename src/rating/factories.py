import factory

from .models import Rating


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating

    name = factory.Faker("sentence")
    description = factory.Faker("text")
