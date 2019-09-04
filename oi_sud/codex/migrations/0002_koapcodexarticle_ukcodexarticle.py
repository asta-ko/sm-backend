# Generated by Django 2.2 on 2019-04-24 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KoapCodexArticle',
            fields=[
            ],
            options={
                'verbose_name': 'Статья КОАП',
                'verbose_name_plural': 'Статьи КОАП',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('codex.codexarticle',),
        ),
        migrations.CreateModel(
            name='UKCodexArticle',
            fields=[
            ],
            options={
                'verbose_name': 'Статья УК',
                'verbose_name_plural': 'Статьи УК',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('codex.codexarticle',),
        ),
    ]