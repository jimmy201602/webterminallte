# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-09-29 06:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommandLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now=True, verbose_name='date time')),
                ('command', models.CharField(max_length=255, verbose_name='command')),
            ],
            options={
                'ordering': ['-datetime'],
                'permissions': (('can_view_command_log', 'Can view command log info'),),
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('end_time', models.DateTimeField(auto_created=True, auto_now=True, verbose_name='End time')),
                ('server', models.GenericIPAddressField(protocol='ipv4', verbose_name='Server IP')),
                ('channel', models.CharField(editable=False, max_length=100, unique=True, verbose_name='Channel name')),
                ('log', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Log name')),
                ('start_time', models.DateTimeField(auto_now_add=True, verbose_name='Start time')),
                ('is_finished', models.BooleanField(default=False, verbose_name='Is finished')),
                ('user', models.CharField(max_length=255, verbose_name='User')),
                ('width', models.PositiveIntegerField(default=90, verbose_name='Width')),
                ('height', models.PositiveIntegerField(default=40, verbose_name='Height')),
            ],
            options={
                'ordering': ['-start_time'],
                'permissions': (('can_delete_log', 'Can delete log info'), ('can_view_log', 'Can view log info'), ('can_play_log', 'Can play record')),
            },
        ),
        migrations.AddField(
            model_name='commandlog',
            name='log',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Log', verbose_name='Log'),
        ),
    ]
