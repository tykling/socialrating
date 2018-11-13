import factory
from faker import Faker
import random

from .models import Rating
from item.models import Item
from actor.models import Actor

fake = Faker()


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating

