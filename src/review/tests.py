import factory
import random

from django.urls import reverse

from item.tests import ItemViewTestCase
from item.models import Item
from .factories import ReviewFactory


class ReviewViewTestCase(ItemViewTestCase):
    """ Shared setUp method for all TestCases for review.views """

    def setUp(self):
        """ The setUp method is run before each test """
        # make sure to call ReviewViewTestCase.setUp() so we have
        # some teams, contexts, categories and items to work with
        super().setUp()

        # create 3-5 reviews per item
        for item in Item.objects.all():
            for i in range(1, random.randint(3, 5)):
                _ = ReviewFactory(
                    item=item,
                    actor=item.team.members.all().order_by("?").first(),
                    context=item.team.contexts.all().order_by("?").first(),
                )

        # remember a review for later
        self.review = self.item.reviews.first()
        self.detail_url = self.review.get_absolute_url()

        # save data to create a new review
        self.review_data = {
            "item": self.item,
            "context": self.item.team.contexts.all().order_by("?").first().id,
            "headline": factory.Faker("sentence").generate(),
            "body": factory.Faker("text").generate(),
        }

        # save data to update Review
        self.update_data = {
            "context": self.item.team.contexts.all().order_by("?").first().id,
            "headline": factory.Faker("sentence").generate(),
            "body": factory.Faker("text").generate(),
        }

        # define other urls
        self.list_url = reverse(
            "team:category:item:review:list",
            kwargs={
                "team_slug": self.item.team.slug,
                "category_slug": self.item.category.slug,
                "item_slug": self.item.slug,
            },
        )
        self.create_url = reverse(
            "team:category:item:review:create",
            kwargs={
                "team_slug": self.item.team.slug,
                "category_slug": self.item.category.slug,
                "item_slug": self.item.slug,
            },
        )
        self.update_url = reverse(
            "team:category:item:review:update",
            kwargs={
                "team_slug": self.item.team.slug,
                "category_slug": self.item.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.review.uuid,
            },
        )
        self.delete_url = reverse(
            "team:category:item:review:delete",
            kwargs={
                "team_slug": self.item.team.slug,
                "category_slug": self.item.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.review.uuid,
            },
        )


class ReviewListViewTest(ReviewViewTestCase):
    """ Test ReviewListView """

    def test_review_list_member(self):
        """ Assert that all the right reviews are listed for the team admin and regular members"""
        for member in [self.team2_admin, self.team2_member, self.common_member]:
            self.client.force_login(member)
            response = self.client.get(self.list_url)
            self.assertContains(
                response, "Reviews for %s" % self.item.name, status_code=200
            )
            # make sure we list all items for the item
            for review in self.item.reviews.all():
                self.assertContains(response, review.pk)

            # and none of the items for some other item
            item = self.item.category.items.exclude(pk=self.item.pk).first()
            for review in item.reviews.all():
                self.assertNotContains(response, review.pk)

    def test_review_list_nonmember(self):
        """ Assert that non-members can not list reviews """
        self.client.force_login(self.team3_member)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)


class ReviewDetailViewTest(ReviewViewTestCase):
    """ Test ReviewDetailView """

    def test_review_detail_member(self):
        """ Assert that review details are shown to an admin/member """
        for member in [self.team2_admin, self.team2_member]:
            self.client.force_login(member)
            response = self.client.get(self.detail_url)
            self.assertContains(response, self.review.pk, status_code=200)

    def test_review_detail_nonmember(self):
        """ Assert that review details are denied for a non-member """
        self.client.force_login(self.team1_member)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 403)


class ReviewCreateViewTest(ReviewViewTestCase):
    """ Test ReviewCreateView """

    def test_review_create_unauthenticated(self):
        """ Assert that unauthenticated users can not create Reviews """
        # try creating a Review without login
        response = self.client.post(path=self.create_url, data=self.review_data)
        self.assertEqual(response.status_code, 403)

    def test_review_create_nonmember(self):
        """ Assert that non-members can not create Reviews """

        # login the user
        self.client.force_login(self.team1_member)

        # create the item and make sure we get 403
        response = self.client.post(self.create_url, data=self.review_data)
        self.assertEqual(response.status_code, 403)

    def test_review_create_admin(self):
        """ Assert that an admin member can create Reviews """
        # login the user
        self.client.force_login(self.team2_admin)

        # create the item and follow the redirect
        response = self.client.post(self.create_url, data=self.review_data, follow=True)

        # make sure review pk is in the response,
        # and that status_code is 200
        self.assertContains(response, self.review_data["headline"], status_code=200)

        # also check for the messages.success() message
        self.assertContains(response, "Saved review ")

    def test_review_create_member(self):
        """ Assert that a regular team member can create Reviews """
        # login the user
        self.client.force_login(self.team2_member)

        # create the item and follow the redirect
        response = self.client.post(self.create_url, data=self.review_data, follow=True)

        # make sure item name is in the response,
        # and that status_code is 200
        self.assertContains(response, self.review_data["headline"], status_code=200)

        # also check for the messages.success() message
        self.assertContains(response, "Saved review ")


class ReviewUpdateViewTest(ReviewViewTestCase):
    """ Test ReviewUpdateView """

    def test_review_update_unauthenticated(self):
        """ Assert that unauthenticated users can not update reviews """
        # first try updating without login
        response = self.client.post(path=self.update_url, data=self.update_data)
        self.assertEqual(response.status_code, 403)

    def test_review_update_regular_member(self):
        """ Assert that regular team members can not update reviews """
        # login as a regular team member (which is not the review owner)
        self.user = (
            self.review.team.members.filter(memberships__admin=False)
            .exclude(pk=self.review.actor.pk)
            .order_by("?")
            .first()
            .user
        )
        self.client.force_login(self.user)
        # try to update the review
        response = self.client.post(path=self.update_url, data=self.update_data)
        self.assertEqual(response.status_code, 403)

    def test_review_update_admin_member(self):
        """ Assert that admin team members can not update reviews """
        if self.team2_admin == self.review.actor.user:
            # the admin happens to be the owner, skip this test
            # this time because it will fail
            return
        # login as the team admin user
        self.client.force_login(self.team2_admin)
        response = self.client.post(path=self.update_url, data=self.update_data)
        self.assertEqual(response.status_code, 403)

    def test_review_update_member_other_team(self):
        """ Assert that regular or admin members of other teams can not update reviews """
        for member in [self.team1_member, self.team1_admin]:
            self.client.force_login(self.team1_member)
            response = self.client.post(path=self.update_url, data=self.update_data)
            self.assertEqual(response.status_code, 403)

    def test_review_update_owner(self):
        """ Assert that the review owner can update reviews """
        # login as the review owner
        self.client.force_login(self.review.actor.user)
        response = self.client.post(
            path=self.update_url, data=self.update_data, follow=True
        )
        # make sure review headline is in the response,
        # and that status_code is 200
        self.assertContains(response, self.update_data["headline"], status_code=200)

        # also check for the messages.success() message
        self.assertContains(response, "Updated review ")


class ReviewDeleteViewTest(ReviewViewTestCase):
    """ Test ReviewDeleteView """

    def test_review_delete_unauthenticated(self):
        """ Assert that unauthenticated users can not delete Reviews """
        response = self.client.post(path=self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_review_delete_member(self):
        """ Assert that regular teammembers can not delete Reviews """
        self.client.force_login(
            self.review.team.members.filter(memberships__admin=False)
            .exclude(pk=self.review.actor.uuid)
            .order_by("?")
            .first()
            .user
        )
        response = self.client.post(path=self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_review_delete_admin(self):
        """ Assert that team admins can delete reviews """
        self.client.force_login(self.team2_admin)
        response = self.client.post(path=self.delete_url, follow=True)
        # did we get redirected to the review list view?
        self.assertContains(
            response, "Reviews for %s" % self.review.item.name, status_code=200
        )

        # did the review disappear from the list?
        self.assertNotContains(response, self.review.headline)
        # do we have the success message?
        self.assertContains(response, "Review has been deleted")

    def test_review_delete_author(self):
        """ Assert that review authors can delete reviews """
        self.client.force_login(self.review.actor.user)
        response = self.client.post(path=self.delete_url, follow=True)
        # did we get redirected to the review list view?
        self.assertContains(
            response, "Reviews for %s" % self.review.item.name, status_code=200
        )

        # did the review disappear from the list?
        self.assertNotContains(response, self.review.headline)
        # do we have the success message?
        self.assertContains(response, "Review has been deleted")
