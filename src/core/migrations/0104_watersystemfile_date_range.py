# Generated by Django 4.1.2 on 2023-11-24 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0103_rename_color_watermaterial_color1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersystemfile',
            name='date_range',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
