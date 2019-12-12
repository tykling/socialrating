import factory
from django.urls import reverse

from review.tests import ReviewViewTestCase
from category.models import Category
from .models import Rating
from .factories import RatingFactory


class RatingViewTestCase(ReviewViewTestCase):
    """ Shared setUp method for all TestCases for rating.views """

    def setUp(self):
        """ The setUp method is run before each test """
        # make sure to call ReviewViewTestCase.setUp() so we have some
        # stuff to work with
        super().setUp()

        # create 3 ratings for each category
        for category in Category.objects.all():
            for i in range(1, 3):
                rating = RatingFactory(category=category)

        # remember the last rating and its detail url
        self.rating = rating
        self.detail_url = rating.get_absolute_url()

        # save data to create new rating
        self.rating_data = {
            "name": factory.Faker("word").generate(),
            "description": factory.Faker("sentence").generate(),
        }

        # define other urls
        self.list_url = reverse(
            "team:category:rating:list",
            kwargs={
                "team_slug": self.team2.slug,
                "category_slug": self.team2_category3.slug,
            },
        )
        self.create_url = reverse(
            "team:category:rating:create",
            kwargs={
                "team_slug": self.team2.slug,
                "category_slug": self.team2_category3.slug,
            },
        )
        self.update_url = reverse(
            "team:category:rating:update",
            kwargs={
                "team_slug": self.rating.team.slug,
                "category_slug": self.rating.category.slug,
                "rating_slug": self.rating.slug,
            },
        )
        self.delete_url = reverse(
            "team:category:rating:delete",
            kwargs={
                "team_slug": self.rating.team.slug,
                "category_slug": self.rating.category.slug,
                "rating_slug": self.rating.slug,
            },
        )


class RatingListViewTest(RatingViewTestCase):
    """ Test RatingListView """

    def test_rating_list_member(self):
        """ Assert that all the right ratings are listed for the team admin and regular members"""
        for member in [self.team2_admin, self.team2_member, self.common_member]:
            self.client.force_login(member)
            response = self.client.get(self.list_url)
            self.assertContains(
                response,
                "Ratings for Category %s" % self.team2_category3.name,
                status_code=200,
            )
            # make sure we list all ratings for this category
            for rating in self.team2_category3.ratings.all():
                self.assertContains(response, rating.name)
            # and none of the others
            for rating in Rating.objects.exclude(
                uuid__in=self.team2_category3.ratings.all().values_list(
                    "uuid", flat=True
                )
            ):
                self.assertNotContains(response, rating.name)

    def test_rating_list_nonmember(self):
        """ Assert that non-members can not list ratings """
        self.client.force_login(self.team3_member)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)
