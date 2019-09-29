# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
try:
    import simplejson as json
except ImportError:
    import json
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
import random
import string


class Log(models.Model):
    server = models.GenericIPAddressField(
        protocol='ipv4', verbose_name=_('Server IP'))
    channel = models.CharField(max_length=100, verbose_name=_(
        'Channel name'), blank=False, unique=True, editable=False)
    log = models.UUIDField(max_length=100, default=uuid.uuid4, verbose_name=_(
        'Log name'), blank=False, unique=True, editable=False)
    start_time = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Start time'))
    end_time = models.DateTimeField(
        auto_created=True, auto_now=True, verbose_name=_('End time'))
    is_finished = models.BooleanField(
        default=False, verbose_name=_('Is finished'))
    loginuser = models.CharField(max_length=255, verbose_name=_('Login User'))
    user = models.CharField(max_length=255, verbose_name=_('Server User'))
    width = models.PositiveIntegerField(default=90, verbose_name=_('Width'))
    height = models.PositiveIntegerField(
        default=40, verbose_name=_('Height'))

    class Meta:
        permissions = (
            ("can_delete_log", _("Can delete log info")),
            ("can_view_log", _("Can view log info")),
            ("can_play_log", _("Can play record")),
        )
        ordering = [
            ('-start_time')
        ]


class CommandLog(models.Model):
    log = models.ForeignKey(Log, verbose_name=_('Log'))
    datetime = models.DateTimeField(
        auto_now=True, verbose_name=_('date time'))
    command = models.CharField(max_length=255, verbose_name=_('command'))

    class Meta:
        permissions = (
            ("can_view_command_log", _("Can view command log info")),
        )
        ordering = [
            ('-datetime')
        ]

    def __str__(self):
        return self.log.user
