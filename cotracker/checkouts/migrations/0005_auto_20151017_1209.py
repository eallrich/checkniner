# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkouts', '0004_auto_20150801_1152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airstrip',
            name='bases',
            field=models.ManyToManyField(to='checkouts.Airstrip', blank=True),
        ),
    ]
