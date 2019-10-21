from django.urls import reverse

from team.tests import TeamViewTestCase
from .factories import ContextFactory


class ContextViewTestCase(TeamViewTestCase):
    """ Shared setUp method for all TestCases for context.views """

    def setUp(self):
        """ The setUp method is run before each test """
        # make sure to call TeamViewTestCase.setUp() so we have some teams to work with
        super().setUp()

        # create contexts
        for team in [self.team1, self.team2]:
            for i in range(1, 3):
                context = ContextFactory(team=team)
        # remember the last context and its url
        self.team2_context3 = context
        self.detail_url = context.get_absolute_url()

        # save data to create new context
        self.context_data = {
            "name": "A new context",
            "description": "A new context description",
        }

        # define other urls
        self.list_url = reverse(
            "team:context:list", kwargs={"team_slug": self.team1.slug}
        )
        self.create_url = reverse(
            "team:context:create", kwargs={"team_slug": self.team1.slug}
        )
        self.update_url = reverse(
            "team:context:update",
            kwargs={
                "team_slug": self.team2.slug,
                "context_slug": self.team2_context3.slug,
            },
        )
        self.delete_url = reverse(
            "team:context:delete",
            kwargs={
                "team_slug": self.team2.slug,
                "context_slug": self.team2_context3.slug,
            },
        )


class ContextListViewTest(ContextViewTestCase):
    """ Test ContextListView """

    def test_context_list_admin(self):
        """ Assert that all contexts are listed for the team admin """
        self.client.force_login(self.team1_admin)
        response = self.client.get(self.list_url)
        self.assertContains(
            response, "Contexts for %s" % self.team1.name, status_code=200
        )
        # make sure we list all contexts for team1
        for context in self.team1.contexts.all():
            self.assertContains(response, context.name)
            self.assertContains(response, context.description)
        # and none for team2
        for context in self.team2.contexts.all():
            self.assertNotContains(response, context.name)

    def test_context_list_member(self):
        """ Assert that all right contexts are listed for the team member """
        for member in [self.team1_member, self.common_member]:
            self.client.force_login(member)
            response = self.client.get(self.list_url)
            self.assertContains(
                response, "Contexts for %s" % self.team1.name, status_code=200
            )
            # make sure we list all contexts for team1
            for context in self.team1.contexts.all():
                self.assertContains(response, context.name)
                self.assertContains(response, context.description)
            # and none for team2
            for context in self.team2.contexts.all():
                self.assertNotContains(response, context.name)

    def test_context_list_nonmember(self):
        """ Assert that non-members can not list contexts """
        self.client.force_login(self.team3_member)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)


class ContextDetailViewTest(ContextViewTestCase):
    """ Test ContextDetailView """

    def test_context_detail_admin(self):
        """ Assert that context details is shown to an admin """
        self.client.force_login(self.team2_admin)
        response = self.client.get(self.detail_url)
        self.assertContains(
            response, "Details for Context %s" % self.team2_context3, status_code=200
        )
        self.assertContains(response, self.team2_context3.description)

    def test_context_detail_member(self):
        """ Assert that context details is shown to a regular member """
        self.client.force_login(self.team2_member)
        response = self.client.get(self.detail_url)
        self.assertContains(
            response, "Details for Context %s" % self.team2_context3, status_code=200
        )
        self.assertContains(response, self.team2_context3.description)

    def test_context_detail_nonmember(self):
        """ Assert that context details denied for a non-member """
        self.client.force_login(self.team1_member)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 403)


class ContextCreateViewTest(ContextViewTestCase):
    """ Test ContextCreateView """

    def test_context_create_unauthenticated(self):
        """ Assert that unauthenticated users can not create Contexts """
        # try creating without login
        response = self.client.post(path=self.create_url, data=self.context_data)
        self.assertEqual(response.status_code, 403)

    def test_context_create_admin(self):
        """ Assert that team admin can create Contexts """

        # login the user
        self.client.force_login(self.team1_admin)

        # create the context and follow the redirect
        response = self.client.post(
            self.create_url, data=self.context_data, follow=True
        )

        # make sure context name is in the response, and that status_code is 200
        self.assertContains(response, self.context_data["name"], status_code=200)

        # also check for context description and the messages.success() message
        self.assertContains(response, self.context_data["description"])
        self.assertContains(response, "New context created!")

    def test_context_create_member(self):
        """ Assert that team member can not create Contexts """

        # login the user
        self.client.force_login(self.team1_member)

        # create the context and follow the redirect
        response = self.client.post(self.create_url, data=self.context_data)
        self.assertEqual(response.status_code, 403)

    def test_context_create_nonmember(self):
        """ Assert that non-members can not create Contexts """

        # login the user
        self.client.force_login(self.team2_member)

        # create the context and follow the redirect
        response = self.client.post(
            self.create_url, data=self.context_data, follow=True
        )
        self.assertEqual(response.status_code, 403)


class ContextUpdateViewTest(ContextViewTestCase):
    """ Test ContextUpdateView """

    def test_context_update_unauthenticated(self):
        """ Assert that unauthenticated users can not update contexts """
        # first try updating without login
        response = self.client.post(path=self.update_url, data=self.context_data)
        self.assertEqual(response.status_code, 403)

    def test_context_update_regular_member(self):
        # login as a regular team member
        self.client.force_login(self.team2_member)
        response = self.client.post(path=self.update_url, data=self.context_data)
        self.assertEqual(response.status_code, 403)

    def test_context_update_regular_member_other_team(self):
        # login as a regular team member of another team
        self.client.force_login(self.team1_member)
        response = self.client.post(path=self.update_url, data=self.context_data)
        self.assertEqual(response.status_code, 403)

    def test_context_update_admin_member(self):
        # login as the team admin user
        self.client.force_login(self.team2_admin)
        response = self.client.post(
            path=self.update_url, data=self.context_data, follow=True
        )
        # check for the new context name and description and the messages.success() message
        self.assertContains(response, self.context_data["name"], status_code=200)
        self.assertContains(response, self.context_data["description"])
        self.assertContains(response, "Context updated!")

    def test_context_update_admin_member_other_team(self):
        # login as the team admin user
        self.client.force_login(self.team1_admin)
        response = self.client.post(path=self.update_url, data=self.team3_data)
        self.assertEqual(response.status_code, 403)


class ContextDeleteViewTest(ContextViewTestCase):
    """ Test ContextDeleteView """

    def test_context_delete_unauthenticated(self):
        response = self.client.post(path=self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_context_delete_nonmember(self):
        self.client.force_login(self.team1_member)
        response = self.client.post(path=self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_context_delete_member(self):
        self.client.force_login(self.team2_member)
        response = self.client.post(path=self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_context_delete_admin(self):
        self.client.force_login(self.team2_admin)
        response = self.client.post(path=self.delete_url, follow=True)
        self.assertContains(response, "Contexts for %s" % self.team2, status_code=200)
        self.assertNotContains(response, self.team2_context3.name)
        self.assertContains(response, "Context has been deleted")
