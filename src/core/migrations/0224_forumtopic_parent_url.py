# Generated by Django 3.0.6 on 2020-07-10 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0223_auto_20200709_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumtopic',
            name='parent_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
