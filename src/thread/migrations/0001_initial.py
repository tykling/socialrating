# Generated by Django 2.2.6 on 2019-11-21 20:51

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [("forum", "0001_initial"), ("actor", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Thread",
            fields=[
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="The date and time when this object was created.",
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="The date and time when this object was last updated.",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "subject",
                    models.CharField(
                        help_text="The subject of this Thread.", max_length=100
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="The slug for this Thread. Must be unique in the Forum."
                    ),
                ),
                (
                    "locked",
                    models.BooleanField(
                        default=False,
                        help_text="Check to lock this Thread to prevent new Comments from being posted to it.",
                    ),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        help_text="The Actor who made this Thread.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="threads",
                        to="actor.Actor",
                    ),
                ),
                (
                    "forum",
                    models.ForeignKey(
                        help_text="The Forum to which this Thread belongs",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="threads",
                        to="forum.Forum",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "permissions": (("add_comment", "Add Comment in this Thread"),),
                "get_latest_by": "created",
                "abstract": False,
            },
        )
    ]
