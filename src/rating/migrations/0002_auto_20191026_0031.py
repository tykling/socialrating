# Generated by Django 2.2.6 on 2019-10-26 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("rating", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="rating",
            name="created",
            field=models.DateTimeField(
                help_text="The date and time when this object was created."
            ),
        ),
        migrations.AlterField(
            model_name="rating",
            name="updated",
            field=models.DateTimeField(
                help_text="The date and time when this object was last updated."
            ),
        ),
    ]
