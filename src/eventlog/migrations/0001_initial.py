# Generated by Django 2.2.6 on 2019-10-16 21:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("actor", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
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
                    "event_type",
                    models.CharField(
                        choices=[
                            ("CREATE", "Create"),
                            ("UPDATE", "Update"),
                            ("DELETE", "Delete"),
                        ],
                        help_text="The type of event.",
                        max_length=6,
                    ),
                ),
                (
                    "object_id",
                    models.CharField(
                        help_text="The PK/UUID of the object this Event relates to.",
                        max_length=32,
                    ),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        help_text="The Actor who caused this event.",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="actor.Actor",
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        help_text="The Django content_type of the model for the object this Event relates to.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="events",
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
        )
    ]
