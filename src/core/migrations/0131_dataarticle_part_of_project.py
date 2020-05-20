# Generated by Django 3.0.3 on 2020-05-20 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0130_dataarticle_recordhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataarticle',
            name='part_of_project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Project'),
            preserve_default=False,
        ),
    ]
