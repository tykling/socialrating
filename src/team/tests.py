from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group

from actor.factories import UserFactory
from team.factories import TeamFactory, MembershipFactory
from team.models import Team

class TeamViewTestCase(TestCase):
    """ Shared setUp method for most TestCases for team.views """

    def setUp(self):
        """ The setUp method is run before each test """
        # create a few test users
        self.team1_admin = UserFactory()
        self.team1_member = UserFactory()
        self.team2_admin = UserFactory()
        self.team2_member = UserFactory()
        self.team3_admin = UserFactory()
        self.team3_member = UserFactory()

        # login the first user
        self.client.force_login(self.team1_admin)

        # create team 1
        self.team1_data = {
            'name': "TestTeam 1",
            'description': "A test team 1",
        }
        response = self.client.post(
            path=reverse("team:create"),
            data=self.team1_data,
        )
        self.team1 = Team.objects.get(name=self.team1_data['name'])

        # login the second user
        self.client.force_login(self.team2_admin)

        # create team 2
        self.team2_data = {
            'name': "TestTeam 2",
            'description': "A test team 2",
        }
        response = self.client.post(
            path=reverse("team:create"),
            data=self.team2_data,
        )
        self.team2 = Team.objects.get(name=self.team2_data['name'])

        self.team3_data={
            'name': "TestTeam 3",
            'description': "A test team 3",
        }

        self.createurl = reverse("team:create")
        self.loginurl = reverse("account_login")
        self.updateurl = reverse("team:update", kwargs={'team_slug': self.team1.slug})

        self.client.logout()


class TeamListViewTest(TeamViewTestCase):
    """ Test TeamListView """

    def test_team_list(self):
        """ Assert that all teams are listed """
        self.client.force_login(self.team1_admin)
        response = self.client.get(reverse('team:list'))
        # make sure we list team1 but not team2
        self.assertContains(response, self.team1.name, status_code=200)
        self.assertNotContains(response, self.team2.name)


class TeamCreateViewTest(TeamViewTestCase):
    """ Test TeamCreateView """

    def test_team_create_unauthenticated(self):
        """ Assert that unauthenticated users can not create Teams """
        # try creating without login
        response = self.client.post(
            self.createurl,
            data=self.team3_data,
        )

        # we should get redirected to the login page with a 'next' url
        self.assertRedirects(response, "%s?next=%s" % (
            self.loginurl,
            self.createurl,
        ))


    def test_team_create_authenticated(self):
        """ Assert that authenticated users can create Teams """

        # login the user
        self.client.force_login(self.team3_admin)

        # create the team and follow the redirect
        response = self.client.post(
            self.createurl,
            data=self.team3_data,
            follow=True,
        )

        # make sure team name is in the response, and that status_code is 200
        self.assertContains(response, self.team3_data['name'], status_code=200)

        # also check for team description and the messages.success() message
        self.assertContains(response, self.team3_data['description'])
        self.assertContains(response, "New team created!")


    def test_team_creator_becomes_founder(self):
        """ Assert that the team creator becomes team founder """

        self.client.force_login(self.team3_admin)

        response = self.client.post(
            path=self.createurl,
            data=self.team3_data,
            follow=True,
        )
        self.team3 = Team.objects.get(name=self.team3_data['name'])

        self.assertContains(response, self.team3_data['description'], status_code=200)

        self.assertEqual(self.team3_admin.actor, self.team3.founder)


    def test_team_creator_becomes_team_member_and_team_admin(self):
        """ Assert that the team creator becomes a team member and admin """

        self.client.force_login(self.team3_admin)

        response = self.client.post(
            path=self.createurl,
            data=self.team3_data,
            follow=True,
        )
        self.team3 = Team.objects.get(name=self.team3_data['name'])

        self.assertTrue(self.team3_admin.actor in self.team3.members.all())
        self.assertTrue(self.team3_admin.actor in self.team3.adminmembers.all())


    def test_team_groups(self):
        """ Assert that the two Django groups are created when a Team is created, and that the team creator is a member of both groups. """
        self.client.force_login(self.team3_admin)

        response = self.client.post(
            path=self.createurl,
            data=self.team3_data,
        )
        self.team3 = Team.objects.get(name=self.team3_data['name'])

        group = Group.objects.get(name=self.team3.name)
        admingroup = Group.objects.get(name=self.team3.name + " Admins")

        self.assertEqual(self.team3.group, group)
        self.assertEqual(self.team3.admingroup, admingroup)
        self.assertTrue(self.team3.group in self.team3.founder.user.groups.all())
        self.assertTrue(self.team3.admingroup in self.team3.founder.user.groups.all())


class TeamUpdateViewTest(TeamViewTestCase):
    """ Test TeamUpdateView """

    def test_team_update_unauthenticated(self):
        """ Assert that unauthenticated users can not update teams """
        # first try updating without login
        response = self.client.post(
            path=self.updateurl,
            data=self.team3_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_team_update_regular_member(self):
        # login as a regular team member
        self.client.force_login(self.team1_member)
        response = self.client.post(
            path=self.updateurl,
            data=self.team3_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_team_update_regular_member_other_team(self):
        # login as a regular team member of another team
        self.client.force_login(self.team2_member)
        response = self.client.post(
            path=self.updateurl,
            data=self.team3_data,
        )
        self.assertEqual(response.status_code, 403)


    def test_team_update_admin_member(self):
        # login as the team admin user
        self.client.force_login(self.team1_admin)
        response = self.client.post(
            path=self.updateurl,
            data=self.team3_data,
            follow=True,
        )
        # check for the new team description and the messages.success() message
        self.assertContains(response, self.team3_data['description'], status_code=200)
        self.assertContains(response, "Team updated!")
        # Make sure the name was not updated
        self.assertNotContains(response, self.team3_data['name'])


    def test_team_update_admin_member_other_team(self):
        # login as the team admin user
        self.client.force_login(self.team2_admin)
        response = self.client.post(
            path=self.updateurl,
            data=self.team3_data,
        )
        self.assertEqual(response.status_code, 403)

