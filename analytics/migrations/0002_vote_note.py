# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-26 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='note',
            field=models.CharField(default='', max_length=128),
        ),
    ]