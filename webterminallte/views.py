from django.views.generic import View
from django.shortcuts import render_to_response, HttpResponse
from django.http import JsonResponse
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
from common.utils import get_redis_instance, EnDeCrypt
from common.models import Log, CommandLog
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from common.views import LoginRequiredMixin
import traceback
import re
import uuid
import logging
import ast
logger = logging.getLogger(__name__)


class SshLogPlay(DetailView):
    model = Log
    template_name = 'webterminal/sshlogplay.html'

    def get_context_data(self, **kwargs):
        context = super(SshLogPlay, self).get_context_data(**kwargs)
        objects = kwargs['object']
        context['logpath'] = '{0}{1}-{2}-{3}/{4}'.format(
            MEDIA_URL, objects.start_time.year, objects.start_time.month, objects.start_time.day, objects.log)
        return context


class SshTerminalMonitor(DetailView):
    model = Log
    template_name = 'webterminal/sshlogmonitor.html'
    raise_exception = True


class SshTerminalKill(View):

    def post(self, request):
        if request.is_ajax():
            channel_name = request.POST.get('channel_name', None)
            try:
                data = Log.objects.get(channel=channel_name)
                if data.is_finished:
                    return JsonResponse({'status': False, 'message': 'Ssh terminal does not exist!'})
                else:
                    data.end_time = now()
                    data.is_finished = True
                    data.save()

                    queue = get_redis_instance()
                    redis_channel = queue.pubsub()
                    if '_' in channel_name:
                        queue.publish(channel_name.rsplit(
                            '_')[0], json.dumps(['close']))
                    else:
                        queue.publish(channel_name, json.dumps(['close']))
                    return JsonResponse({'status': True, 'message': 'Terminal has been killed !'})
            except ObjectDoesNotExist:
                return JsonResponse({'status': False, 'message': 'Request object does not exist!'})


class SshConnect(TemplateView):
    template_name = 'webterminal/ssh.html'

    def get_context_data(self, **kwargs):
        context = super(SshConnect, self).get_context_data(**kwargs)
        context['ip'] = self.kwargs.get('ip')
        context['serverid'] = self.kwargs.get('serverid')
        return context


class InitialSshApi(View):

    def post(self, **kwargs):
        if request.is_ajax():
            data = request.POST.get("data", None)
            if data:
                try:
                    endeins = EnDeCrypt()
                    data = ast.literal_eval(endeins.decrypt(data))
                    temp_key = uuid.uuid4().hex
                    cache_data = {
                        "nickname": data.get("nickname"),
                        "ip": data.get("ip"),
                        "port": data.get("port"),
                        "public_ip": data.get("public_ip", None),
                        "private_ip": data.get("private_ip", None),
                        "admin_user": data.get("admin_user"),
                        "system_user": data.get("system_user"),
                        "user_key": data.get("user_key")
                    }
                    # get redis connection
                    conn = get_redis_instance()
                    conn.set(temp_key, json.dumps(cache_data))
                    conn.expire(temp_key, 60)
                    return JsonResponse({'status': True, 'message': 'Success!', "key": temp_key})
                except Exception:
                    return JsonResponse({'status': False, 'message': 'Illegal data!'})
        return JsonResponse({'status': False, 'message': 'Illegal request or data!'})
