# Generated by Django 3.1.2 on 2020-12-22 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_course_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='position',
            field=models.PositiveSmallIntegerField(db_index=True, help_text='Enter 0 to make this the annual summary'),
        ),
    ]
