# Generated by Django 2.2.6 on 2019-10-17 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0011_update_proxy_permissions"),
        ("actor", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Membership",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The date and time when this object was created.",
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The date and time when this object was last updated.",
                    ),
                ),
                (
                    "admin",
                    models.BooleanField(
                        default=False, help_text="This member is an admin of this Team"
                    ),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        help_text="The Actor to which this Membership belongs",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="memberships",
                        to="actor.Actor",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The date and time when this object was created.",
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The date and time when this object was last updated.",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the Team. Make it short and memorable.",
                        max_length=128,
                    ),
                ),
                (
                    "description",
                    models.TextField(help_text="A short description of this team."),
                ),
                (
                    "slug",
                    models.SlugField(help_text="The slug for this Team", unique=True),
                ),
                (
                    "admingroup",
                    models.OneToOneField(
                        help_text="The Django Group for admin members of this Team",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="adminteam",
                        to="auth.Group",
                    ),
                ),
                (
                    "founder",
                    models.ForeignKey(
                        help_text="The founder of this Team",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="founded_teams",
                        to="actor.Actor",
                    ),
                ),
                (
                    "group",
                    models.OneToOneField(
                        help_text="The Django Group for all members of this Team",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="team",
                        to="auth.Group",
                    ),
                ),
                (
                    "members",
                    models.ManyToManyField(
                        help_text="The current members of this Team",
                        related_name="teams",
                        through="team.Membership",
                        to="actor.Actor",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "permissions": (
                    ("add_category", "Add Category belonging to this Team"),
                    ("add_context", "Add Context belonging to this Team"),
                ),
            },
        ),
        migrations.AddField(
            model_name="membership",
            name="team",
            field=models.ForeignKey(
                help_text="The Group to which this Membership belongs",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="memberships",
                to="team.Team",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="membership", unique_together={("actor", "team")}
        ),
    ]
