# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Slang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(unique=True, max_length=64, verbose_name='Нормальная форма матерного слова')),
            ],
            options={
                'verbose_name': 'Матерное слово',
                'verbose_name_plural': 'Матерные слова',
            },
            bases=(models.Model,),
        ),
    ]
