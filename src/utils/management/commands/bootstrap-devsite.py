import logging, random

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from eav.models import EnumValue, EnumGroup, Attribute

from actor.models import Actor, User
from actor.factories import UserFactory

from team.models import Team, Membership
from team.factories import TeamFactory, MembershipFactory

from category.models import Category

logger = logging.getLogger("socialrating.%s" % __name__)


class Command(BaseCommand):
    args = 'none'
    help = 'Create mock data for socialrating development instances'

    def handle(self, *args, **options):
        logger.info('Bootstrapping database with mock data...')

        # add Users (which then adds actors)
        self.mock(
            model=User,
            factory=UserFactory,
            count=100,
            bulk=False
        )

        # add admin
        admin = User.objects.create(
            username="admin",
            is_staff=True,
            is_superuser=True,
        )
        admin.set_password("admin")
        admin.save()

        ####################
        # add car team
        carteam = Team.objects.create(
            name='Car Nerds',
            founder=Actor.objects.all().order_by('?').first()
        )

        # add categories for carteam
        makecat = Category.objects.create(
            team=carteam,
            name='Car Maker',
            description='A car maker.',
        )
        carcat = Category.objects.create(
            team=carteam,
            name='Car',
            description='A car.',
        )


        # add attributes for "Car Maker" category
        Attribute.objects.create(
            name='Country',
            datatype=Attribute.TYPE_TEXT,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=makecat.id,
            required=True,
            slug=makecat.create_attribute_slug('Country'),
            description='The country this car maker is from',
        )

        # add attributes for "Car Model" category
        Attribute.objects.create(
            name='Make',
            datatype=Attribute.TYPE_OBJECT,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=carcat.id,
            required=True,
            slug=carcat.create_attribute_slug('Make'),
            description='The make of this car',
            extra_data='category.id=%s' % makecat.id,
        )
        Attribute.objects.create(
            name='Colour',
            datatype=Attribute.TYPE_TEXT,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=carcat.id,
            required=True,
            slug=carcat.create_attribute_slug('Colour'),
            description='The colour of this car',
        )
        Attribute.objects.create(
            name='BHP',
            datatype=Attribute.TYPE_INT,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=carcat.id,
            required=True,
            slug=carcat.create_attribute_slug('BHP'),
            description='The BHP of this car',
        )
        Attribute.objects.create(
            name='Date Seen',
            datatype=Attribute.TYPE_DATE,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=carcat.id,
            slug=carcat.create_attribute_slug('Date Seen'),
            description='The date and time this car was seen',
        )

        # add car makers
        ford = makecat.items.create(
            name='Ford',
            eav__category1_country='US'
        )
        bmw = makecat.items.create(
            name='BMW',
            eav__category1_country='DE'
        )
        peugeot = makecat.items.create(
            name='Peugeot',
            eav__category1_country='FR'
        )

        # add cars
        carcat.items.create(
            name='Escort RS Cosworth',
            eav__category2_make=ford,
            eav__category2_colour='black',
            eav__category2_bhp='170',
            eav__category2_date_seen=timezone.now(),
        )
        carcat.items.create(
            name='Focus',
            eav__category2_make=ford,
            eav__category2_colour='blue',
            eav__category2_bhp='95',
            eav__category2_date_seen=timezone.now(),
        )
        carcat.items.create(
            name='520i E34',
            eav__category2_make=bmw,
            eav__category2_colour='purple',
            eav__category2_bhp='200',
            eav__category2_date_seen=timezone.now(),
        )
        carcat.items.create(
            name='M3',
            eav__category2_make=bmw,
            eav__category2_colour='white',
            eav__category2_bhp='280',
            eav__category2_date_seen=timezone.now(),
        )
        carcat.items.create(
            name='406 Estate',
            eav__category2_make=peugeot,
            eav__category2_colour='white',
            eav__category2_bhp='130',
            eav__category2_date_seen=timezone.now(),
        )


        ####################
        # add foodies team
        foodteam = Team.objects.create(
            name='Foodies',
            founder=Actor.objects.all().order_by('?').first()
        )

        # add categories for foodteam
        restaurant = Category.objects.create(
            team=foodteam,
            name='Restaurant',
            description='A place where food is served',
        )
        dish = Category.objects.create(
            team=foodteam,
            name='Dish',
            description='Some food',
        )

        # add attributes for "Restaurant" category
        Attribute.objects.create(
            name='Location',
            datatype=Attribute.TYPE_TEXT,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=restaurant.id,
            required=True,
            slug=restaurant.create_attribute_slug('Location'),
            description='The location of this restaurant',
        )
        Attribute.objects.create(
            name='Description',
            datatype=Attribute.TYPE_TEXT,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=restaurant.id,
            required=True,
            slug=restaurant.create_attribute_slug('Description'),
            description='A short description of this restaurant. Markdown should be supported.',
        )

        # add attributes for "Dish" category
        Attribute.objects.create(
            name='Price',
            datatype=Attribute.TYPE_INT,
            entity_ct=ContentType.objects.get(app_label='category', model='category'),
            entity_id=restaurant.id,
            required=True,
            slug=restaurant.create_attribute_slug('Price'),
            description='The price in EUR of this dish',
        )

        # add restaurants


        ####################
        # add music team
        musicteam = Team.objects.create(
            name='Music Lovers',
            founder=Actor.objects.all().order_by('?').first()
        )


        ###################
        # add team members for all teams
        for team in Team.objects.all():
            # add team founders and site admin as team admin members
            Membership.objects.create(
                team=team,
                actor=team.founder,
                admin=True
            )

            Membership.objects.create(
                team=team,
                actor=admin.actor,
                admin=True
            )

            # add non-admin team members
            membercount = random.randint(1, int(Actor.objects.count() / Team.objects.count()))
            logger.info("creating %s non-admin members of team %s" % (membercount, team))
            self.mock(
                model=Membership,
                factory=MembershipFactory,
                count=membercount,
                team=team,
            )

        # add Actors with no team to a randon team
        for actor in Actor.objects.filter(membership__isnull=True):
            Membership.objects.create(
                team=Team.objects.all().order_by('?').first(),
                actor=actor,
            )

        logger.info('Done. A superuser was added, username admin password admin. Django admin access and member of all teams. Enjoy!')


    def mock(self, model, factory, count, chunksize=10, bulk=True, **kwargs):
        """
        The mock function has two modes of operation, bulk or not.
        Djangos bulk_create method is fast but does not call the .save() method,
        and does not trigger signals. Use bulk if possible, it is much faster.
        """
        logger.info("Creating %s instances of model %s using factory %s and kwargs %s" % (count, model, factory, kwargs))
        if bulk:
            for i in range(0, count, chunksize):
                chunk_items = factory.build_batch(count-i if count-i < chunksize else chunksize, **kwargs)
                model.objects.bulk_create(chunk_items)
                if i:
                    logger.debug("Mocked %s objects in %s" % (i, model))
        else:
            for i in range(0, count):
                item = factory.build(**kwargs)
                item.save()

