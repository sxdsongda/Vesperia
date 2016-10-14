# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-01 08:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_auto_20160831_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vm_set', to='assets.Server', verbose_name='\u5bbf\u4e3b\u673a'),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='vm_type',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='\u865a\u62df\u673a\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='networkdevice',
            name='device_type',
            field=models.CharField(choices=[('router', '\u8def\u7531\u5668'), ('switch', '\u4ea4\u6362\u673a'), ('firewall', '\u9632\u706b\u5899'), ('NLB', 'NetScaler'), ('wireless', '\u65e0\u7ebfAP')], default='router', max_length=64, verbose_name='\u8bbe\u5907\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='software',
            name='version',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='\u7248\u672c'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='interface_type',
            field=models.CharField(choices=[('sata', 'SATA'), ('sas', 'SAS'), ('scsi', 'SCSI'), ('ddr3', 'DDR3'), ('ddr4', 'DDR4')], default='sata', max_length=16, verbose_name='\u63a5\u53e3\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='macaddress',
            field=models.CharField(max_length=64, unique=True, verbose_name='MAC\u5730\u5740'),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='manage_ip',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='\u7ba1\u7406IP'),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='os_release',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='\u7cfb\u7edf\u7248\u672c'),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='os_type',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='\u7cfb\u7edf\u7c7b\u578b'),
        ),
        migrations.AlterUniqueTogether(
            name='virtualmachine',
            unique_together=set([]),
        ),
        migrations.AlterIndexTogether(
            name='virtualmachine',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='virtualmachine',
            name='host_on',
        ),
    ]