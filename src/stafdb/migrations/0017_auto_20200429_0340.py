# Generated by Django 3.0.3 on 2020-04-29 03:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stafdb', '0016_referencespace_geocodes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name_plural': 'activities'},
        ),
        migrations.AlterModelOptions(
            name='activitycatalog',
            options={'verbose_name_plural': 'activity catalogs'},
        ),
        migrations.RemoveField(
            model_name='activitycatalog',
            name='url',
        ),
    ]
