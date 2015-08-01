# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('checkouts', '0003_auto_20150801_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pilotweight',
            name='pilot',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
