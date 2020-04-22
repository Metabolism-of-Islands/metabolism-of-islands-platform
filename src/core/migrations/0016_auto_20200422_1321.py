# Generated by Django 3.0.3 on 2020-04-22 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20200422_1208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='is_public',
        ),
        migrations.AddField(
            model_name='tag',
            name='belongs_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Record'),
        ),
    ]
