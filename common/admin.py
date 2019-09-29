from __future__ import absolute_import, division, print_function, unicode_literals
from django.contrib import admin
from common.models import Log, CommandLog


class LogAdmin(admin.ModelAdmin):
    list_display = ["server", "loginuser","user", "start_time", "end_time"]


class CommandLogAdmin(admin.ModelAdmin):
    list_display = ["loguser", "command", "datetime"]

    def loguser(self, object):
        return object.log.user
    loguser.admin_order_field = 'log__user'


admin.site.register(Log, LogAdmin)
admin.site.register(CommandLog, CommandLogAdmin)
