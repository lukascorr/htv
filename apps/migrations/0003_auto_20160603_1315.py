# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 13:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_topic_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='twitter_id',
            field=models.BigIntegerField(),
        ),
    ]
