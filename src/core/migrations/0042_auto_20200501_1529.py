# Generated by Django 3.0.3 on 2020-05-01 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20200501_1521'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='record_ptr',
        ),
        migrations.RemoveField(
            model_name='moocprogress',
            name='video',
        ),
        migrations.AddField(
            model_name='libraryitem',
            name='is_part_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LibraryItem'),
        ),
        migrations.DeleteModel(
            name='MOOCVideo',
        ),
        migrations.DeleteModel(
            name='Video',
        ),
    ]
