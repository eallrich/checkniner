# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('checkouts', '0002_pilotweight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pilotweight',
            name='pilot',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE, unique=True),
        ),
    ]
