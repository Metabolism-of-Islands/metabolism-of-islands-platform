# Generated by Django 3.0.3 on 2020-06-15 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0170_projectdesign_header_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarydataset',
            name='size',
            field=models.IntegerField(blank=True, help_text='Size in MB', null=True),
        ),
    ]
