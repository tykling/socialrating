import factory

from actor.models import Actor
from item.models import Item
from context.models import Context
from .models import Review


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    actor = factory.Iterator(Actor.objects.all())
    item = factory.Iterator(Item.objects.all())
    context = factory.Iterator(Context.objects.all())
    headline = factory.Faker("sentence")
    body = factory.Faker("text")
