# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-05-10 00:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drawing', '0002_auto_20161220_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aoi',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='windenergysite',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
    ]
