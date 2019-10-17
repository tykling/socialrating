# Generated by Django 2.2.6 on 2019-10-17 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='The date and time when this object was created.')),
                ('updated', models.DateTimeField(auto_now_add=True, help_text='The date and time when this object was last updated.')),
                ('name', models.CharField(help_text='The name of this Rating. Must be unique within this Category.', max_length=100)),
                ('slug', models.SlugField(help_text='The slug for this Rating. Must be unique within this Category.', max_length=100)),
                ('description', models.CharField(help_text='Describe what users should consider when voting for this Rating. Please keep it to 255 characters or less.', max_length=255)),
                ('max_rating', models.PositiveIntegerField(default=5, help_text='The highest possible vote for this rating. Minimum 2, defaults to 5, maximum 100.')),
                ('icon', models.CharField(default='fas fa-star', help_text='The icon to use when visually displaying the votes for this rating.', max_length=50)),
                ('category', models.ForeignKey(help_text='The Category on which this Item is based', on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='category.Category')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'category'), ('slug', 'category')},
            },
        ),
    ]
