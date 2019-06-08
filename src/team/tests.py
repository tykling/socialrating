from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group

from actor.factories import UserFactory
from team.factories import TeamFactory, MembershipFactory
from team.models import Team


class TeamCreateViewTest(TestCase):
    """ Test TeamCreateView """

    def setUp(self):
        """ The setUp method is run before each test """
        # create a test user
        self.user = UserFactory()

        # put the form data together
        self.team_name = "TestTeam"
        self.team_description = "A test team"
        self.formdata = {
            'name': self.team_name,
            'description': self.team_description,
        }

        # the URL we are working with
        self.url = reverse("team:create")


    def test_team_create_unauthenticated(self):
        """ Assert that unauthenticated users can not create Teams """
        # try creating without login
        response = self.client.post(
            self.url,
            data=self.formdata,
        )

        # we should get redirected to the login page with a 'next' url
        self.assertRedirects(response, "%s?next=%s" % (
            reverse("account_login"),
            self.url,
        ))


    def test_team_create_authenticated(self):
        """ Assert that authenticated users can create Teams """

        # login the user
        self.client.force_login(self.user)

        # create the team and follow the redirect
        response = self.client.post(
            self.url,
            data=self.formdata,
            follow=True,
        )

        # make sure team name is in the response, and that status_code is 200
        self.assertContains(response, self.team_name, status_code=200)

        # also check for team description and the messages.success() message
        self.assertContains(response, self.team_description)
        self.assertContains(response, "New team created!")


    def test_team_creator_becomes_founder(self):
        """ Assert that the team creator becomes team founder """

        self.client.force_login(self.user)

        response = self.client.post(
            path=self.url,
            data=self.formdata,
            follow=True,
        )

        self.assertContains(response, "A test team", status_code=200)
        self.team = Team.objects.first()

        self.assertEqual(self.user.actor, self.team.founder)


    def test_team_creator_becomes_team_member_and_team_admin(self):
        """ Assert that the team creator becomes a team member and admin """

        self.client.force_login(self.user)

        response = self.client.post(
            path=self.url,
            data=self.formdata,
            follow=True,
        )

        team = Team.objects.first()
        self.assertTrue(self.user.actor in team.members.all())
        self.assertTrue(self.user.actor in team.adminmembers.all())


    def test_team_groups(self):
        """ Assert that two Django groups are created when a Team is created, and that the team creator is a member of both groups. """
        self.client.force_login(self.user)

        response = self.client.post(
            path=self.url,
            data=self.formdata,
            follow=True,
        )

        team = Team.objects.first()
        group = Group.objects.get(name=team.name)
        admingroup = Group.objects.get(name=team.name + " Admins")

        self.assertEqual(team.group, group)
        self.assertEqual(team.admingroup, admingroup)
        self.assertTrue(team.group in team.founder.user.groups.all())
        self.assertTrue(team.admingroup in team.founder.user.groups.all())


class TeamUpdateViewTest(TestCase):
    """ Test TeamUpdateView """

    def setUp(self):
        """ The setUp method is run before each test """
        # create a test user
        self.team1_admin = UserFactory()
        self.team1_member = UserFactory()
        self.team2_admin = UserFactory()
        self.team2_member = UserFactory()

        # put the form data together
        self.team_name = "TestTeam 1"

        # login the user
        self.client.force_login(self.team1_admin)

        # create team 1
        response = self.client.post(
            path=reverse("team:create"),
            data={
                'name': "TestTeam 1",
                'description': "A test team 1",
            }
        )
        self.team1 = Team.objects.get(name="TestTeam 1")

        # login the other user
        self.client.force_login(self.team2_admin)

        # create team 2
        response = self.client.post(
            path=reverse("team:create"),
            data={
                'name': "TestTeam 2",
                'description': "A test team 2",
            }
        )
        self.team2 = Team.objects.get(name="TestTeam 2")

        self.formdata = {
                'description': "New description",
        }

        self.url = reverse("team:update", kwargs={'team_slug': self.team1.slug})

    def test_team_update_unauthenticated(self):
        """ Assert that unauthenticated users can not update teams """
        # first try updating without login
        response = self.client.post(
            path=self.url,
            data=self.formdata,
        )
        self.assertEqual(response.status_code, 403)


    def test_team_update_regular_member(self):
        # login as a regular team member
        self.client.force_login(self.team1_member)
        response = self.client.post(
            path=self.url,
            data=self.formdata,
        )
        self.assertEqual(response.status_code, 403)


    def test_team_update_regular_member_other_team(self):
        # login as a regular team member of another team
        self.client.force_login(self.team2_member)
        response = self.client.post(
            path=self.url,
            data=self.formdata,
        )
        self.assertEqual(response.status_code, 403)


    def test_team_update_admin_member(self):
        # login as the team admin user
        self.client.force_login(self.team1_admin)
        response = self.client.post(
            path=self.url,
            data=self.formdata,
            follow=True,
        )
        # check for the new team description and the messages.success() message
        self.assertContains(response, "New description", status_code=200)
        self.assertContains(response, "Team updated!")


    def test_team_update_admin_member_other_team(self):
        # login as the team admin user
        self.client.force_login(self.team2_admin)
        response = self.client.post(
            path=self.url,
            data=self.formdata,
        )
        self.assertEqual(response.status_code, 403)

