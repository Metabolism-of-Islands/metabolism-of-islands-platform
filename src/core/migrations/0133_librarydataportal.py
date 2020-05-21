# Generated by Django 3.0.3 on 2020-05-21 12:00

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0132_librarydataset'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibraryDataPortal',
            fields=[
                ('libraryitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.LibraryItem')),
                ('portal_software', models.CharField(blank=True, max_length=50, null=True)),
            ],
            bases=('core.libraryitem',),
            managers=[
                ('objects_unfiltered', django.db.models.manager.Manager()),
            ],
        ),
    ]
