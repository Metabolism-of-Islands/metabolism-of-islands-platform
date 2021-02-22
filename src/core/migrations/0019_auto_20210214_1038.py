# Generated by Django 3.1.2 on 2021-02-14 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_cityloopsindicator_cityloopsindicatorvalue'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='flowdiagram',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='recordrelationship',
            name='relationship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='core.relationship'),
        ),
    ]
