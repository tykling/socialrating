# Generated by Django 2.2.6 on 2019-11-21 20:51

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("utils", "0001_initial"),
        ("rating", "0002_auto_20191121_2051"),
        ("taggit", "0003_taggeditem_add_unique_index"),
        ("review", "0002_review_tags"),
    ]

    operations = [
        migrations.CreateModel(
            name="Vote",
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
                    "vote",
                    models.PositiveIntegerField(
                        help_text="The actual numerical vote for this Rating."
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        blank=True,
                        help_text="An optional short comment related to this specific vote. 1000 character limit.",
                        max_length=1000,
                        null=True,
                    ),
                ),
                (
                    "rating",
                    models.ForeignKey(
                        help_text="The Rating this Vote applies to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="rating.Rating",
                    ),
                ),
                (
                    "review",
                    models.ForeignKey(
                        help_text="The Review this Vote belongs to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="review.Review",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="utils.UUIDTaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": "created",
                "abstract": False,
                "unique_together": {("review", "rating")},
            },
        )
    ]
