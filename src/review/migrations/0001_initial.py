# Generated by Django 2.2 on 2019-04-30 12:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("context", "0001_initial"),
        ("item", "0001_initial"),
        ("actor", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
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
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "headline",
                    models.CharField(
                        help_text="A short headline for this review", max_length=100
                    ),
                ),
                (
                    "body",
                    models.TextField(
                        blank=True,
                        help_text="The text review. Optional. Markdown is supported (or will be at some point).",
                        null=True,
                    ),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        help_text="The Actor who made this Review",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reviews",
                        to="actor.Actor",
                    ),
                ),
                (
                    "context",
                    models.ForeignKey(
                        help_text="The Context to which this Review belongs.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="context.Context",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        help_text="The Item this Review applies to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="item.Item",
                    ),
                ),
            ],
            options={"ordering": ["-created"]},
        )
    ]
