# Generated by Django 4.1.2 on 2025-04-04 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0107_rename_uploader_contact_libraryitem_contact_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libraryitem',
            name='data_type',
        ),
        migrations.DeleteModel(
            name='DatasetType',
        ),
    ]
