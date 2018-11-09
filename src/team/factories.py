import factory
from faker import Faker

from django.contrib.auth.hashers import make_password

from .models import Team, Membership
from actor.models import Actor


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Faker('company')
    founder = factory.Iterator(Actor.objects.all())


class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Membership

    actor = factory.Iterator(Actor.objects.all())
    team = factory.Iterator(Team.objects.all())

