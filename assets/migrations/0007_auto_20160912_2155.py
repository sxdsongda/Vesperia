# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-12 13:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0006_auto_20160906_2300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disk',
            name='iface_type',
            field=models.CharField(choices=[('ATA', 'SATA'), ('SAS', 'SAS'), ('SCSI', 'SCSI'), ('IDE', 'IDE')], default='SAS', max_length=64, verbose_name='\u63a5\u53e3\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='disk',
            name='sn',
            field=models.CharField(default=django.utils.timezone.now, max_length=128, verbose_name='SN\u53f7'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='newassetapprovalzone',
            name='asset_type',
            field=models.CharField(blank=True, choices=[('server', '\u670d\u52a1\u5668'), ('network_device', '\u7f51\u7edc\u8bbe\u5907'), ('storage', '\u5b58\u50a8\u8bbe\u5907'), ('virtual_machine', '\u865a\u62df\u673a')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='newassetapprovalzone',
            name='status',
            field=models.CharField(choices=[('Success', '\u5df2\u901a\u8fc7'), ('Failed', '\u5ba1\u6279\u5931\u8d25'), ('SuccessWithProblems', '\u5b58\u5728\u95ee\u9898'), ('NotYet', '\u672a\u5ba1\u6279')], default='NotYet', max_length=64, verbose_name='\u5ba1\u6279\u72b6\u6001'),
        ),
        migrations.AlterField(
            model_name='nic',
            name='macaddress',
            field=models.CharField(max_length=64, verbose_name='MAC'),
        ),
        migrations.AlterField(
            model_name='ram',
            name='sn',
            field=models.CharField(default=django.utils.timezone.now, max_length=128, verbose_name='SN\u53f7'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='disk',
            unique_together=set([('asset', 'sn'), ('asset', 'slot')]),
        ),
        migrations.AlterUniqueTogether(
            name='nic',
            unique_together=set([('asset', 'macaddress')]),
        ),
        migrations.AlterUniqueTogether(
            name='raidadaptor',
            unique_together=set([('asset', 'sn'), ('asset', 'slot')]),
        ),
        migrations.AlterUniqueTogether(
            name='ram',
            unique_together=set([('asset', 'sn'), ('asset', 'slot')]),
        ),
    ]
