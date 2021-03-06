# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-31 09:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='language',
            field=models.CharField(blank=True, choices=[('cn', '\u4e2d\u6587'), ('en', '\u82f1\u6587')], max_length=32, null=True, verbose_name='\u8bed\u8a00'),
        ),
        migrations.AlterField(
            model_name='software',
            name='platform',
            field=models.CharField(blank=True, choices=[('Windows', 'Windows'), ('Linux', 'Linux'), ('MacOS', 'MacOS')], max_length=32, null=True, verbose_name='\u8fd0\u884c\u5e73\u53f0'),
        ),
        migrations.AlterField(
            model_name='software',
            name='software_type',
            field=models.CharField(blank=True, choices=[('system', '\u64cd\u4f5c\u7cfb\u7edf'), ('application', '\u5e94\u7528\u8f6f\u4ef6')], max_length=64, null=True, verbose_name='\u8f6f\u4ef6\u7c7b\u578b'),
        ),
    ]
