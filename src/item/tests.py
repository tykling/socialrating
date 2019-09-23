import factory, random

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group

from category.tests import CategoryViewTestCase
from category.models import Category

from .factories import ItemFactory


class ItemViewTestCase(CategoryViewTestCase):
    """ Shared setUp method for all TestCases for item.views """

    def setUp(self):
        """ The setUp method is run before each test """
        # make sure to call CategoryViewTestCase.setUp() so we have
        # some teams, contexts and categories to work with
        super().setUp()

        # create 3-5 items per category
        for category in Category.objects.all():
            for i in range(1,random.randint(3,5)):
                item = ItemFactory(category=category)

        # remember an item for later
        self.item = self.team2_category3.items.first()
        self.detail_url = self.item.get_absolute_url()

        # save data to create a new item
        self.item_data = {
            'name': factory.Faker('sentence').generate(),
        }

        # define other urls
        self.list_url = reverse("team:category:item:list", kwargs={
            'team_slug': self.item.team.slug,
            'category_slug': self.item.category.slug,
        })
        self.create_url = reverse("team:category:item:create", kwargs={
            'team_slug': self.item.team.slug,
            'category_slug': self.item.category.slug,
        })
        self.update_url = reverse("team:category:item:update", kwargs={
            'team_slug': self.item.team.slug,
            'category_slug': self.item.category.slug,
            'item_slug': self.item.slug,
        })
        self.delete_url = reverse("team:category:item:delete", kwargs={
            'team_slug': self.item.team.slug,
            'category_slug': self.item.category.slug,
            'item_slug': self.item.slug,
        })


class ItemListViewTest(ItemViewTestCase):
    """ Test ItemListView """

    def test_item_list_member(self):
        """ Assert that all the right items are listed for the team admin and regular members"""
        for member in [self.team2_admin, self.team2_member, self.common_member]:
            self.client.force_login(member)
            response = self.client.get(self.list_url)
            self.assertContains(
                response,
                "Items in Category %s" % self.item.category.name,
                status_code=200
            )
            # make sure we list all items for the category
            for item in self.item.category.items.all():
                self.assertContains(response, item.name)
            # and none of the items from some other category
            for item in self.team2.categories.exclude(
                pk=self.item.category.pk
            ).first().items.all():
                self.assertNotContains(response, item.name)


    def test_item_list_nonmember(self):
        """ Assert that non-members can not list items """
        self.client.force_login(self.team3_member)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)


class ItemDetailViewTest(ItemViewTestCase):
    """ Test ItemDetailView """

    def test_item_detail_member(self):
        """ Assert that item details are shown to an admin and member """
        for member in [self.team2_admin, self.team2_member]:
            self.client.force_login(member)
            response = self.client.get(self.detail_url)
            self.assertContains(
                response,
                "%s is an Item in the Category %s." % (
                    self.item.name,
                    self.item.category.name
                ),
                status_code=200
            )


    def test_item_detail_nonmember(self):
        """ Assert that item details denied for a non-member """
        self.client.force_login(self.team1_member)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 403)


class ItemCreateViewTest(ItemViewTestCase):
    """ Test ItemCreateView """

    def test_item_create_unauthenticated(self):
        """ Assert that unauthenticated users can not create Items """
        # try creating without login
        response = self.client.post(
            path=self.create_url,
            data=self.item_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_item_create_admin(self):
        """ Assert that an admin member can create Items """
        # login the user
        self.client.force_login(self.team2_admin)

        # create the item and follow the redirect
        response = self.client.post(
            self.create_url,
            data=self.item_data,
            follow=True,
        )

        # make sure item name is in the response, and that status_code is 200
        self.assertContains(response, self.item_data['name'], status_code=200)

        # also check for the messages.success() message
        self.assertContains(response, "New Item created!")

    def test_item_create_member(self):
        """ Assert that a regular team member can create Items """
        # login the user
        self.client.force_login(self.team2_member)

        # create the item and follow the redirect
        response = self.client.post(
            self.create_url,
            data=self.item_data,
            follow=True,
        )

        # make sure item name is in the response, and that status_code is 200
        self.assertContains(response, self.item_data['name'], status_code=200)

        # also check for the messages.success() message
        self.assertContains(response, "New Item created!")


    def test_item_create_nonmember(self):
        """ Assert that non-members can not create Items """

        # login the user
        self.client.force_login(self.team1_member)

        # create the item and make sure we get 403
        response = self.client.post(
            self.create_url,
            data=self.item_data,
        )
        self.assertEqual(response.status_code, 403)


class ItemUpdateViewTest(ItemViewTestCase):
    """ Test ItemUpdateView """

    def test_item_update_unauthenticated(self):
        """ Assert that unauthenticated users can not update items """
        # first try updating without login
        response = self.client.post(
            path=self.update_url,
            data=self.item_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_item_update_regular_member(self):
        """ Assert that regular team members can update items """
        # login as a regular team member
        self.client.force_login(self.team2_member)
        #print("posting to %s" % self.update_url)
        response = self.client.post(
            path=self.update_url,
            data=self.item_data,
            follow=True,
        )
        # check for the new item name and the messages.success() message
        self.assertContains(response, self.item_data['name'], status_code=200)
        self.assertContains(response, "Item updated!")


    def test_item_update_admin_member(self):
        """ Assert that team admins can update items """
        # login as the team admin user
        self.client.force_login(self.team2_admin)
        response = self.client.post(
            path=self.update_url,
            data=self.item_data,
            follow=True,
        )
        # check for the new item name and the messages.success() message
        self.assertContains(response, self.item_data['name'], status_code=200)
        self.assertContains(response, "Item updated!")


    def test_team_update_regular_member_other_team(self):
        """ Assert that regular members of other teams can not update items """
        # login as a regular team member of another team
        self.client.force_login(self.team1_member)
        response = self.client.post(
            path=self.update_url,
            data=self.item_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_item_update_admin_member_other_team(self):
        """ Assert that admins of other teams can not update items """
        self.client.force_login(self.team1_admin)
        response = self.client.post(
            path=self.update_url,
            data=self.item_data,
        )
        self.assertEqual(response.status_code, 403)


class ItemDeleteViewTest(ItemViewTestCase):
    """ Test ItemDeleteView """

    def test_item_delete_unauthenticated(self):
        """ Assert that unauthenticated users can not delete Items """
        response = self.client.post(
            path=self.delete_url,
        )
        self.assertEqual(response.status_code, 403)


    def test_item_delete_nonmember(self):
        """ Assert that non teammembers can not delete Items """
        self.client.force_login(self.team1_member)
        response = self.client.post(
            path=self.delete_url,
        )
        self.assertEqual(response.status_code, 403)


    def test_item_delete_member(self):
        """ Assert that regular teammembers can not delete Items """
        self.client.force_login(self.team2_member)
        response = self.client.post(
            path=self.delete_url,
        )
        self.assertEqual(response.status_code, 403)

    def test_item_delete_admin(self):
        """ Assert that team admins can delete items """
        self.client.force_login(self.team2_admin)
        response = self.client.post(
            path=self.delete_url,
            follow=True,
        )
        # did we get redirected to the item list view?
        self.assertContains(response, "Items in Category %s" % self.item.category.name, status_code=200)
        # did the item disappear from the list?
        self.assertNotContains(response, self.item.name)
        # do we have the success message?
        self.assertContains(response, "Item has been deleted")

