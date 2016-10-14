# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-25 04:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=64, unique=True, verbose_name='email address')),
                ('name', models.CharField(max_length=32, verbose_name='\u59d3\u540d')),
                ('token', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('tel', models.IntegerField(blank=True, default=None, null=True, verbose_name='\u5ea7\u673a')),
                ('mobile', models.IntegerField(blank=True, default=None, null=True, verbose_name='\u624b\u673a')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='\u751f\u65e5')),
                ('memo', models.TextField(blank=True, default=None, max_length=500, null=True, verbose_name='\u5907\u6ce8')),
                ('date_joined', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u4fe1\u606f',
                'verbose_name_plural': '\u7528\u6237\u4fe1\u606f',
            },
        ),
    ]
