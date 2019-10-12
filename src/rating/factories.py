import factory
import random

from .models import Rating
from item.models import Item
from actor.models import Actor


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating

    name = factory.Faker("sentence")
    description = factory.Faker("text")
