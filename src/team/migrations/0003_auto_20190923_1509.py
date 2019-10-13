# Generated by Django 2.2.2 on 2019-09-23 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("team", "0002_auto_20190610_0908")]

    operations = [
        migrations.AlterModelOptions(
            name="team",
            options={
                "ordering": ["name"],
                "permissions": (
                    ("add_category", "Add Category belonging to this Team"),
                    ("add_context", "Add Context belonging to this Team"),
                ),
            },
        )
    ]