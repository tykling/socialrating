# Generated by Django 2.2.6 on 2019-11-21 20:51

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("utils", "0001_initial"),
        ("team", "0001_initial"),
        ("taggit", "0003_taggeditem_add_unique_index"),
        ("actor", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="tags",
            field=taggit.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="utils.UUIDTaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AddField(
            model_name="membership",
            name="actor",
            field=models.ForeignKey(
                help_text="The Actor to which this Membership belongs",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="memberships",
                to="actor.Actor",
            ),
        ),
        migrations.AddField(
            model_name="membership",
            name="tags",
            field=taggit.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="utils.UUIDTaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
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
