# Generated by Django 2.2.6 on 2019-10-17 18:58

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rating', '0001_initial'),
        ('review', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, help_text='The date and time when this object was created.')),
                ('updated', models.DateTimeField(auto_now_add=True, help_text='The date and time when this object was last updated.')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('vote', models.PositiveIntegerField(help_text='The actual numerical vote for this Rating.')),
                ('comment', models.CharField(blank=True, help_text='An optional short comment related to this specific vote. 255 character limit.', max_length=255, null=True)),
                ('rating', models.ForeignKey(help_text='The Rating this Vote applies to.', on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='rating.Rating')),
                ('review', models.ForeignKey(help_text='The Review this Vote belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='review.Review')),
            ],
            options={
                'ordering': ['pk'],
                'unique_together': {('review', 'rating')},
            },
        ),
    ]
