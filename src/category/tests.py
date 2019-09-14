import factory

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group

from actor.factories import UserFactory
from context.tests import ContextViewTestCase

from .factories import CategoryFactory

class CategoryViewTestCase(ContextViewTestCase):
    """ Shared setUp method for all TestCases for category.views """

    def setUp(self):
        """ The setUp method is run before each test """
        # make sure to call ContextViewTestCase.setUp() so we have some teams and contexts to work with
        super().setUp()

        # create categories
        for team in [self.team1, self.team2]:
            for i in range(1,3):
                category = CategoryFactory(team=team)

        # remember the last category and its url
        self.team2_category3 = category
        self.detail_url = category.get_absolute_url()

        # save data to create new category
        self.category_data = {
            'name': factory.Faker('word').generate(),
            'description': factory.Faker('sentence').generate(),
        }

        # define other urls
        self.list_url = reverse("team:category:list", kwargs={'team_slug': self.team1.slug})
        self.create_url = reverse("team:category:create", kwargs={'team_slug': self.team1.slug})
        self.update_url = reverse("team:category:update", kwargs={
            'team_slug': self.team2.slug,
            'category_slug': self.team2_category3.slug,
        })
        self.delete_url = reverse("team:category:delete", kwargs={
            'team_slug': self.team2.slug,
            'category_slug': self.team2_category3.slug,
        })


class CategoryListViewTest(CategoryViewTestCase):
    """ Test CategoryListView """

    def test_category_list_member(self):
        """ Assert that all the right categories are listed for the team admin and regular members"""
        for member in [self.team1_admin, self.team1_member, self.common_member]:
            self.client.force_login(member)
            response = self.client.get(self.list_url)
            self.assertContains(response, "Categories for %s" % self.team1.name, status_code=200)
            # make sure we list all categories for team1
            for category in self.team1.categories.all():
                self.assertContains(response, category.name)
            # and none of team2s categories
            for category in self.team2.categories.all():
                self.assertNotContains(response, category.name)


    def test_category_list_nonmember(self):
        """ Assert that non-members can not list categories """
        self.client.force_login(self.team3_member)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)


class CategoryDetailViewTest(CategoryViewTestCase):
    """ Test CategoryDetailView """

    def test_category_detail_admin(self):
        """ Assert that category details are shown to an admin """
        self.client.force_login(self.team2_admin)
        response = self.client.get(self.detail_url)
        self.assertContains(response, "Details for Category %s" % self.team2_category3, status_code=200)
        self.assertContains(response, self.team2_category3.description)


    def test_category_detail_member(self):
        """ Assert that category details are shown to a regular member """
        self.client.force_login(self.team2_member)
        response = self.client.get(self.detail_url)
        self.assertContains(response, "Details for Category %s" % self.team2_category3, status_code=200)
        self.assertContains(response, self.team2_category3.description)


    def test_category_detail_nonmember(self):
        """ Assert that category details denied for a non-member """
        self.client.force_login(self.team1_member)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 403)


class CategoryCreateViewTest(CategoryViewTestCase):
    """ Test CategoryCreateView """

    def test_category_create_unauthenticated(self):
        """ Assert that unauthenticated users can not create Categories """
        # try creating without login
        response = self.client.post(
            path=self.create_url,
            data=self.category_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_category_create_admin(self):
        """ Assert that team admin can create Categories """

        # login the user
        self.client.force_login(self.team1_admin)

        # create the category and follow the redirect
        response = self.client.post(
            self.create_url,
            data=self.category_data,
            follow=True,
        )

        # make sure category name is in the response, and that status_code is 200
        self.assertContains(response, self.category_data['name'], status_code=200)

        # also check for category description and the messages.success() message
        self.assertContains(response, self.category_data['description'])
        self.assertContains(response, "New category created!")


    def test_category_create_member(self):
        """ Assert that a regular team member can not create Categories """

        # login the user
        self.client.force_login(self.team1_member)

        # create the category and make sure we get 403
        response = self.client.post(
            self.create_url,
            data=self.category_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_category_create_nonmember(self):
        """ Assert that non-members can not create Categories """

        # login the user
        self.client.force_login(self.team2_member)

        # create the category and make sure we get 403
        response = self.client.post(
            self.create_url,
            data=self.category_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 403)


class CategoryUpdateViewTest(CategoryViewTestCase):
    """ Test CategoryUpdateView """

    def test_category_update_unauthenticated(self):
        """ Assert that unauthenticated users can not update categories """
        # first try updating without login
        response = self.client.post(
            path=self.update_url,
            data=self.category_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_category_update_regular_member(self):
        """ Assert that regular team members can not update categories """
        # login as a regular team member
        self.client.force_login(self.team2_member)
        response = self.client.post(
            path=self.update_url,
            data=self.category_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_team_update_regular_member_other_team(self):
        """ Assert that regular members of other teams can not update categories """
        # login as a regular team member of another team
        self.client.force_login(self.team1_member)
        response = self.client.post(
            path=self.update_url,
            data=self.category_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_category_update_admin_member(self):
        """ Assert that team admins can update categories """
        # login as the team admin user
        self.client.force_login(self.team2_admin)
        response = self.client.post(
            path=self.update_url,
            data=self.category_data,
            follow=True,
        )
        # check for the new category name and description and the messages.success() message
        self.assertContains(response, self.category_data['name'], status_code=200)
        self.assertContains(response, self.category_data['description'])
        self.assertContains(response, "Category updated!")


    def test_category_update_admin_member_other_team(self):
        """ Assert that admins of other teams can not update categories """
        self.client.force_login(self.team1_admin)
        response = self.client.post(
            path=self.update_url,
            data=self.category_data,
        )
        self.assertEqual(response.status_code, 403)


class CategoryDeleteViewTest(CategoryViewTestCase):
    """ Test CategoryDeleteView """

    def test_category_delete_unauthenticated(self):
        """ Assert that unauthenticated users can not delete Categories """
        response = self.client.post(
            path=self.delete_url,
        )
        self.assertEqual(response.status_code, 403)

    def test_category_delete_nonmember(self):
        """ Assert that non teammembers can not delete Categories """
        self.client.force_login(self.team1_member)
        response = self.client.post(
            path=self.delete_url,
        )
        self.assertEqual(response.status_code, 403)

    def test_category_delete_member(self):
        """ Assert that regular teammembers can not delete Categories """
        self.client.force_login(self.team2_member)
        response = self.client.post(
            path=self.delete_url,
        )
        self.assertEqual(response.status_code, 403)

    def test_category_delete_admin(self):
        """ Assert that team admins can delete categories """
        self.client.force_login(self.team2_admin)
        response = self.client.post(
            path=self.delete_url,
            follow=True,
        )
        # did we get redirected to the category list view?
        self.assertContains(response, "Categories for %s" % self.team2, status_code=200)
        # did the category disappear?
        self.assertNotContains(response, self.team2_category3.name)
        # do we have the success message?
        self.assertContains(response, "Category has been deleted")
