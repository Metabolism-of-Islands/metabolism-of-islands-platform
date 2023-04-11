# Generated by Django 4.1.2 on 2023-04-11 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0084_watersystemspace_alter_watersystemflow_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersystemfile',
            name='is_processed',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.CreateModel(
            name='WaterSystemData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.watersystemcategory')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.watersystemfile')),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.watersystemflow')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.watersystemspace')),
            ],
        ),
    ]
