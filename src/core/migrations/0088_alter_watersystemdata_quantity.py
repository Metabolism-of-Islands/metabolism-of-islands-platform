# Generated by Django 4.1.2 on 2023-04-11 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0087_watersystemdata_timeframe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watersystemdata',
            name='quantity',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
