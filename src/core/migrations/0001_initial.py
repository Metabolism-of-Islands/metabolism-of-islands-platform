# Generated by Django 3.0.3 on 2020-03-20 04:05

from django.conf import settings
import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import stdimage.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='mooc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('desciption', models.TextField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='mooc_answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='mooc_module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('mooc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mooc')),
            ],
        ),
        migrations.CreateModel(
            name='mooc_question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('right_answer', models.IntegerField(db_index=True)),
                ('answer_explanation', models.TextField(blank=True, null=True)),
                ('position', models.PositiveSmallIntegerField(blank=True, db_index=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mooc_module')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('image', stdimage.models.StdImageField(blank=True, null=True, upload_to='records')),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Record')),
                ('slug', models.CharField(db_index=True, max_length=100)),
                ('position', models.PositiveSmallIntegerField(blank=True, db_index=True, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Article')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
            options={
                'ordering': ['position', 'title'],
            },
            bases=('core.record',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Record')),
                ('type', models.CharField(blank=True, choices=[('conference', 'Conference'), ('hackathon', 'Hackathon'), ('workshop', 'Workshop'), ('seminar', 'Seminar'), ('summerschool', 'Summer School'), ('other', 'Other')], max_length=20, null=True)),
                ('url', models.URLField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            bases=('core.record',),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Record')),
                ('date', models.DateField()),
            ],
            options={
                'verbose_name_plural': 'news',
            },
            bases=('core.record',),
        ),
        migrations.CreateModel(
            name='mooc_quiz_answers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mooc_answer')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mooc_question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='mooc_answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mooc_question'),
        ),
        migrations.CreateModel(
            name='ArticleDesign',
            fields=[
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='design', serialize=False, to='core.Article')),
                ('header', models.CharField(choices=[('full', 'Full header with title and subtitle'), ('small', 'Small header; menu only'), ('image', 'Image underneath menu')], default='full', max_length=6)),
                ('header_title', models.CharField(blank=True, max_length=100, null=True)),
                ('header_subtitle', models.CharField(blank=True, max_length=255, null=True)),
                ('header_image', stdimage.models.StdImageField(blank=True, null=True, upload_to='header_image')),
                ('logo', stdimage.models.StdImageField(blank=True, null=True, upload_to='logos')),
                ('custom_css', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Record')),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.URLField(max_length=255)),
                ('embed_code', models.CharField(blank=True, max_length=20, null=True)),
                ('video_site', models.CharField(choices=[('youtube', 'Youtube'), ('vimeo', 'Vimeo'), ('other', 'Other')], max_length=14)),
                ('position', models.PositiveSmallIntegerField(blank=True, db_index=True, null=True)),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.mooc_module')),
            ],
            bases=('core.record',),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Record')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('url', models.URLField(blank=True, max_length=255, null=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
            bases=('core.record',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='People',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Record')),
                ('affiliation', models.CharField(blank=True, max_length=255, null=True)),
                ('site', models.ManyToManyField(to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'people',
            },
            bases=('core.record',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='mooc_progress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Video')),
            ],
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('site', 'slug'), name='site_slug'),
        ),
    ]
