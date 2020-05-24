# Generated by Django 3.0.3 on 2020-05-24 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0143_auto_20200524_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryitem',
            name='language',
            field=models.CharField(choices=[('EN', 'English'), ('ES', 'Spanish'), ('CH', 'Chinese'), ('FR', 'French'), ('GE', 'German'), ('NL', 'Dutch'), ('OT', 'Other'), ('PT', 'Portuguese')], default='EN', max_length=2),
        ),
    ]
