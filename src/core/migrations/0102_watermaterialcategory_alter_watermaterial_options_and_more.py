# Generated by Django 4.1.2 on 2023-11-21 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0101_watermaterial_watersystemdata_material'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterMaterialCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_french', models.CharField(max_length=255)),
                ('name_english', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AlterModelOptions(
            name='watermaterial',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='watermaterial',
            name='color',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='watermaterial',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.watermaterialcategory'),
            preserve_default=False,
        ),
    ]
