# Generated by Django 2.2 on 2019-04-30 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0002_category_default_context'),
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='team',
            field=models.ForeignKey(help_text='The Team to which this Category belongs', on_delete=django.db.models.deletion.PROTECT, related_name='categories', to='team.Team'),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('name', 'team'), ('slug', 'team')},
        ),
    ]