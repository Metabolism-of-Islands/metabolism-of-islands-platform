# Generated by Django 3.1.2 on 2022-09-22 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_libraryitem_part_of_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryitem',
            name='part_of_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='library_items', to='core.project'),
        ),
    ]
