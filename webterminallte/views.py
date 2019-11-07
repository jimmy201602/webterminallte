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
import traceback
import re
import uuid
import logging
import ast
import pytz
from django.utils.translation import activate
logger = logging.getLogger(__name__)


class LogList(ListView):
    def dispatch(self, request, *args, **kwargs):
        activate("zh_hans")
        conn = get_redis_instance()
        if "key" not in kwargs.keys():
            raise PermissionDenied('403 Forbidden')
        login_info = conn.get(kwargs["key"])
        if login_info:
            try:
                login_info = json.loads(login_info)
                self.request.user = login_info.get("nickname", "Anonymous")
            except:
                raise PermissionDenied('403 Forbidden')
        else:
            raise PermissionDenied('403 Forbidden')
        return super(LogList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LogList, self).get_context_data(**kwargs)
        context['key'] = self.kwargs["key"]
        return context

    model = Log
    template_name = 'webterminal/logslist.html'


class CommandLogList(View):

    def dispatch(self, request, *args, **kwargs):
        if "key" not in kwargs.keys():
            raise PermissionDenied('403 Forbidden')
        conn = get_redis_instance()
        login_info = conn.get(kwargs["key"])
        if login_info:
            try:
                login_info = json.loads(login_info)
                self.request.user = login_info.get("nickname", "Anonymous")
            except:
                raise PermissionDenied('403 Forbidden')
        else:
            raise PermissionDenied('403 Forbidden')
        return super(CommandLogList, self).dispatch(request, *args, **kwargs)

    def post(self, request, **kwargs):
        if request.is_ajax():
            id = request.POST.get('id', None)
            data = CommandLog.objects.filter(log__id=id)
            if data.count() == 0:
                return JsonResponse({'status': False, 'message': 'Request object not exist!'})
            return JsonResponse({'status': True, 'message': [{'datetime': i.datetime.astimezone(pytz.timezone("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'), 'command': i.command} for i in data]})
        else:
            return JsonResponse({'status': False, 'message': 'Method not allowed!'})


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

    def get_context_data(self, **kwargs):
        context = super(SshTerminalMonitor, self).get_context_data(**kwargs)
        context['key'] = self.kwargs.get("key","")
        return context


class SshTerminalKill(View):

    def dispatch(self, request, *args, **kwargs):
        activate("zh_hans")
        conn = get_redis_instance()
        if "key" not in kwargs.keys():
            raise PermissionDenied('403 Forbidden')
        login_info = conn.get(kwargs["key"])
        if login_info:
            try:
                login_info = json.loads(login_info)
                self.request.user = login_info.get("nickname", "Anonymous")
            except:
                raise PermissionDenied('403 Forbidden')
        else:
            raise PermissionDenied('403 Forbidden')
        return super(SshTerminalKill, self).dispatch(request, *args, **kwargs)

    def post(self, request,key):
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

    def post(self, request):
        data = self.request.POST.get("data", None)
        if not data:
            try:
                data = json.loads(request.body)
                if isinstance(data, str):
                    data = ast.literal_eval(data)
                data = data.get("data", None)
            except:
                pass
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
                    "user_key": data.get("user_key"),
                    "password": data.get("password", "")
                }
                # get redis connection
                conn = get_redis_instance()
                conn.set(temp_key, json.dumps(cache_data))
                conn.expire(temp_key, 60)
                return JsonResponse({'status': True, 'message': 'Success!', "key": temp_key})
            except Exception as e:
                print(traceback.print_exc())
                return JsonResponse({'status': False, 'message': 'Illegal request or data!', "data": data})
        return JsonResponse({'status': False, 'message': 'Illegal request or data!'})


class InitialLoginApi(View):

    def post(self, request):
        data = self.request.POST.get("data", None)
        if not data:
            try:
                data = json.loads(request.body)
                if isinstance(data, str):
                    data = ast.literal_eval(data)
                data = data.get("data", None)
            except:
                pass
        if data:
            try:
                endeins = EnDeCrypt()
                data = ast.literal_eval(endeins.decrypt(data))
                temp_key = uuid.uuid4().hex
                cache_data = {
                    "nickname": data.get("nickname"),
                    "admin_user": data.get("admin_user"),
                    "system_user": data.get("system_user"),
                }
                # get redis connection
                conn = get_redis_instance()
                conn.set(temp_key, json.dumps(cache_data))
                conn.expire(temp_key, 60 * 30)
                return JsonResponse({'status': True, 'message': 'Success!', "key": temp_key})
            except Exception as e:
                print(traceback.print_exc())
                return JsonResponse({'status': False, 'message': 'Illegal request or data!', "data": data})
        return JsonResponse({'status': False, 'message': 'Illegal request or data!'})
