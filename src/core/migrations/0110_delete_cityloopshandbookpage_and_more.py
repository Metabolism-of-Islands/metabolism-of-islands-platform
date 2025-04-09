# Generated by Django 4.1.2 on 2025-04-09 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0109_merge_20250409_0802'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CityLoopsHandbookPage',
        ),
        migrations.RemoveField(
            model_name='cityloopsindicatorvalue',
            name='city',
        ),
        migrations.RemoveField(
            model_name='cityloopsindicatorvalue',
            name='indicator',
        ),
        migrations.RemoveField(
            model_name='cityloopsscareport',
            name='actors_dataset',
        ),
        migrations.RemoveField(
            model_name='cityloopsscareport',
            name='city',
        ),
        migrations.RemoveField(
            model_name='cityloopsscareport',
            name='land_use_dataset',
        ),
        migrations.RemoveField(
            model_name='cityloopsscareport',
            name='population_dataset',
        ),
        migrations.RemoveField(
            model_name='cityloopsucareport',
            name='city',
        ),
        migrations.RemoveField(
            model_name='cityloopsucareport',
            name='cover_image',
        ),
        migrations.RemoveField(
            model_name='cityloopsucareport',
            name='land_use_dataset',
        ),
        migrations.RemoveField(
            model_name='cityloopsucareport',
            name='materials_dataset',
        ),
        migrations.RemoveField(
            model_name='cityloopsucareport',
            name='population_dataset',
        ),
        migrations.RemoveField(
            model_name='cityloopsucareport',
            name='stock_map_dataset',
        ),
        migrations.RemoveField(
            model_name='eurostatdb',
            name='spaces',
        ),
        migrations.RemoveField(
            model_name='eurostatdb',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='watermaterial',
            name='category',
        ),
        migrations.RemoveField(
            model_name='watersystemcategory',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='watersystemdata',
            name='category',
        ),
        migrations.RemoveField(
            model_name='watersystemdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='watersystemdata',
            name='flow',
        ),
        migrations.RemoveField(
            model_name='watersystemdata',
            name='material',
        ),
        migrations.RemoveField(
            model_name='watersystemdata',
            name='space',
        ),
        migrations.RemoveField(
            model_name='watersystemfile',
            name='category',
        ),
        migrations.RemoveField(
            model_name='watersystemfile',
            name='uploader',
        ),
        migrations.AlterUniqueTogether(
            name='watersystemflow',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='watersystemflow',
            name='category',
        ),
        migrations.RemoveField(
            model_name='watersystemflow',
            name='part_of_flow',
        ),
        migrations.RemoveField(
            model_name='watersystemnode',
            name='category',
        ),
        migrations.RemoveField(
            model_name='watersystemnode',
            name='entry_flows',
        ),
        migrations.RemoveField(
            model_name='watersystemnode',
            name='exit_flows',
        ),
        migrations.DeleteModel(
            name='CityLoopsIndicator',
        ),
        migrations.DeleteModel(
            name='CityLoopsIndicatorValue',
        ),
        migrations.DeleteModel(
            name='CityLoopsSCAReport',
        ),
        migrations.DeleteModel(
            name='CityLoopsUCAReport',
        ),
        migrations.DeleteModel(
            name='EurostatDB',
        ),
        migrations.DeleteModel(
            name='WaterMaterial',
        ),
        migrations.DeleteModel(
            name='WaterMaterialCategory',
        ),
        migrations.DeleteModel(
            name='WaterSystemCategory',
        ),
        migrations.DeleteModel(
            name='WaterSystemData',
        ),
        migrations.DeleteModel(
            name='WaterSystemFile',
        ),
        migrations.DeleteModel(
            name='WaterSystemFlow',
        ),
        migrations.DeleteModel(
            name='WaterSystemNode',
        ),
        migrations.DeleteModel(
            name='WaterSystemSpace',
        ),
    ]
