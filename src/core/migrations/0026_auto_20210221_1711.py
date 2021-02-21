# Generated by Django 3.1.2 on 2021-02-21 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20210221_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryitem',
            name='language',
            field=models.CharField(blank=True, choices=[('EN', 'English'), ('ES', 'Spanish'), ('CH', 'Chinese'), ('FR', 'French'), ('GE', 'German'), ('NL', 'Dutch'), ('PT', 'Portuguese'), ('CT', 'Catalan'), ('FI', 'Finnish'), ('DN', 'Danish'), ('NO', 'Norwegian'), ('OT', 'Other')], default='EN', max_length=2, null=True),
        ),
    ]
