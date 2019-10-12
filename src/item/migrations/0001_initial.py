# Generated by Django 2.2 on 2019-04-30 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("category", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Item",
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
                        help_text="The name of this Item. Must be unique within the Category.",
                        max_length=100,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="The slug for this Item. Must be unique within the Category."
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        help_text="The Category on which this Item is based",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="category.Category",
                    ),
                ),
            ],
            options={
                "unique_together": {("name", "category"), ("slug", "category")},
                "ordering": ["name"],
            },
        )
    ]
