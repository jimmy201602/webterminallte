# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.mixins import AccessMixin
from django.utils.translation import activate
from django.views.generic import View
from django.shortcuts import render_to_response, HttpResponse
from django.http import JsonResponse
from common.models import Log, CommandLog
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
try:
    import simplejson as json
except ImportError:
    import json
from django.contrib import messages as message
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils.encoding import smart_str
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic.detail import DetailView
from django.core.serializers import serialize
from webterminallte.settings import MEDIA_URL
from django.utils.timezone import now
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
import traceback
from django.contrib.auth.views import redirect_to_login
from django.utils.translation import ugettext, ugettext_lazy as _
import pytz
import uuid
from common.utils import get_redis_instance
__webterminalhelperversion__ = '0.3'


class LoginRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user is authenticated.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.handle_no_permission()
        activate(request.LANGUAGE_CODE.replace('-', '_'))
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.raise_exception and self.request.user.is_authenticated():
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

class LogList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Log
    template_name = 'common/logslist.html'
    permission_required = 'common.can_view_log'
    raise_exception = True


class CommandLogList(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'common.can_view_command_log'
    raise_exception = True

    def post(self, request):
        if request.is_ajax():
            id = request.POST.get('id', None)
            data = CommandLog.objects.filter(log__id=id)
            if data.count() == 0:
                return JsonResponse({'status': False, 'message': 'Request object not exist!'})
            if request.LANGUAGE_CODE == 'zh-hans':
                return JsonResponse({'status': True, 'message': [{'datetime': i.datetime.astimezone(pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'), 'command': i.command} for i in data]})
            else:
                return JsonResponse({'status': True, 'message': [{'datetime': i.datetime.strftime('%Y-%m-%d %H:%M:%S'), 'command': i.command} for i in data]})
        else:
            return JsonResponse({'status': False, 'message': 'Method not allowed!'})