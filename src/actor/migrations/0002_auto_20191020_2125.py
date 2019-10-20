# Generated by Django 2.2.6 on 2019-10-20 21:25

import actor.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("actor", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="actor",
            name="user",
            field=models.ForeignKey(
                help_text="The Django User object this Actor belongs to (might be 'deleted' if the User was deleted)",
                on_delete=models.SET(actor.models.get_sentinel_user),
                to=settings.AUTH_USER_MODEL,
            ),
        )
    ]
