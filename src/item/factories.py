import factory

from category.models import Category
from .models import Item


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    name = factory.Faker("sentence")
    category = factory.Iterator(Category.objects.all())
