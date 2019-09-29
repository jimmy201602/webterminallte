# -*- coding: utf-8 -*-
import paramiko
import socket
from channels.generic.websockets import WebsocketConsumer
try:
    import simplejson as json
except ImportError:
    import json
from webterminallte.interactive import interactive_shell, SshTerminalThread, InterActiveShellThread
import sys
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import ast
import time
from django.contrib.auth.models import User
from django.utils.timezone import now
import os
from channels import Group
import traceback
from common.utils import WebsocketAuth, get_redis_instance
from common.models import Log
import logging
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
logger = logging.getLogger(__name__)
import uuid
from six import string_types as basestring
try:
    unicode
except NameError:
    unicode = str


class Webterminal(WebsocketConsumer, WebsocketAuth):

    ssh = paramiko.SSHClient()
    http_user = True
    #http_user_and_session = True
    channel_session = True
    channel_session_user = True

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({"accept": True})
        # set ip and id property to auth
        self.ip = self.kwargs.get("ip", None)
        self.id = self.kwargs.get("id", None)
        if not self.authenticate:
            self.message.reply_channel.send(
                {"text": '\033[1;3;31mYou must login to the system!\033[0m'}, immediately=True)
            self.message.reply_channel.send({"accept": False})

    def disconnect(self, message):
        # close threading
        self.closessh()

        self.message.reply_channel.send({"accept": False})

        audit_log = Log.objects.get(user=User.objects.get(
            username=self.message.user), channel=self.message.reply_channel.name)
        audit_log.is_finished = True
        audit_log.end_time = now()
        audit_log.save()
        self.close()

    @property
    def queue(self):
        queue = get_redis_instance()
        channel = queue.pubsub()
        return queue

    def closessh(self):
        # close threading
        self.queue.publish(self.message.reply_channel.name,
                           json.dumps(['close']))

    def receive(self, text=None, bytes=None, **kwargs):
        self.ip = self.kwargs.get("ip", None)
        self.id = self.kwargs.get("id", None)
        # handle auth
        method = "password"
        username = "root"  # auth server ssh username
        password = "root"
        key = None
        port = 22
        loginuser = "test"  # auth user
        try:
            if text:
                data = json.loads(text)
                begin_time = time.time()
                if isinstance(data, list) and data[0] == 'ip' and len(data) == 5:
                    ip = data[1]
                    width = data[2]
                    height = data[3]
                    id = data[4]
                    self.ssh.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
                    # permission control
                    # self.message.reply_channel.send(
                    # {"text": '\033[1;3;31mYou have not permission to connect server {0}!\033[0m'.format(ip)}, immediately=True)
                    #self.message.reply_channel.send({"accept": False})
                    #logger.error("{0} have not permission to connect server {1}!".format(self.message.user.username, ip))
                    # return
                    try:
                        if method == 'password':
                            self.ssh.connect(
                                ip, port=port, username=username, password=password, timeout=3)
                        else:
                            private_key = StringIO(key)
                            if 'RSA' in key:
                                private_key = paramiko.RSAKey.from_private_key(
                                    private_key)
                            elif 'DSA' in key:
                                private_key = paramiko.DSSKey.from_private_key(
                                    private_key)
                            elif 'EC' in key:
                                private_key = paramiko.ECDSAKey.from_private_key(
                                    private_key)
                            elif 'OPENSSH' in key:
                                private_key = paramiko.Ed25519Key.from_private_key(
                                    private_key)
                            else:
                                self.message.reply_channel.send({"text":
                                                                 '\033[1;3;31munknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type\033[0m'}, immediately=True)
                                self.message.reply_channel.send(
                                    {"accept": False})
                                logger.error(
                                    "unknown or unsupported key type, only support rsa dsa ed25519 ecdsa key type!")
                            self.ssh.connect(
                                ip, port=port, username=username, pkey=private_key, timeout=3)
                        # when connect server sucess record log
                        audit_log = Log.objects.create(
                            user=username, loginuser=loginuser, server=ip, channel=self.message.reply_channel.name, width=width, height=height)
                        audit_log.save()
                    except socket.timeout:
                        self.message.reply_channel.send(
                            {"text": '\033[1;3;31mConnect to server time out\033[0m'}, immediately=True)
                        logger.error(
                            "Connect to server {0} time out!".format(ip))
                        self.message.reply_channel.send({"accept": False})
                        return
                    except Exception as e:
                        self.message.reply_channel.send(
                            {"text": '\033[1;3;31mCan not connect to server: {0}\033[0m'.format(e)}, immediately=True)
                        self.message.reply_channel.send({"accept": False})
                        logger.error(
                            "Can not connect to server {0}: {1}".format(ip, e))
                        return

                    chan = self.ssh.invoke_shell(
                        width=width, height=height, term='xterm')

                    # open a new threading to handle ssh to avoid global variable bug
                    sshterminal = SshTerminalThread(self.message, chan)
                    sshterminal.setDaemon = True
                    sshterminal.start()

                    directory_date_time = now()
                    log_name = os.path.join('{0}-{1}-{2}'.format(directory_date_time.year,
                                                                 directory_date_time.month, directory_date_time.day), '{0}'.format(audit_log.log))

                    # open ssh terminal
                    interactivessh = InterActiveShellThread(
                        chan, self.message.reply_channel.name, log_name=log_name, width=width, height=height)
                    interactivessh.setDaemon = True
                    interactivessh.start()

                elif isinstance(data, list) and data[0] in ['stdin', 'stdout']:
                    self.queue.publish(
                        self.message.reply_channel.name, json.loads(text)[1])
                elif isinstance(data, list) and data[0] == u'set_size':
                    self.queue.publish(self.message.reply_channel.name, text)
                elif isinstance(data, list) and data[0] == u'close':
                    self.disconnect(self.message)
                    return
                else:
                    self.queue.publish(self.message.reply_channel.name, text)
                    logger.error("Unknow command found!")
            elif bytes:
                self.queue.publish(
                    self.message.reply_channel.name, bytes)
        except socket.error:
            audit_log = Log.objects.get(
                user=loginuser, channel=self.message.reply_channel.name)
            audit_log.is_finished = True
            audit_log.end_time = now()
            audit_log.save()
            self.closessh()
            self.close()
        except ValueError:
            self.queue.publish(
                self.message.reply_channel.name, smart_unicode(text))
        except Exception as e:
            logger.error(traceback.print_exc())
            self.closessh()
            self.close()


class SshTerminalMonitor(WebsocketConsumer, WebsocketAuth):

    http_user = True
    http_user_and_session = True
    channel_session = True
    channel_session_user = True

    def connect(self, message, channel):
        """
        User authenticate and detect user has permission to monitor user ssh action!
        """
        if not self.authenticate:
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You must login to the system!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        if not self.haspermission('common.can_monitor_serverinfo'):
            self.message.reply_channel.send({"text": json.dumps(
                {'status': False, 'message': 'You have not permission to monitor user ssh action!'})}, immediately=True)
            self.message.reply_channel.send({"accept": False})
        self.message.reply_channel.send({"accept": True})
        Group(channel).add(self.message.reply_channel.name)

    def disconnect(self, message, channel):
        Group(channel).discard(self.message.reply_channel.name)
        self.message.reply_channel.send({"accept": False})
        self.close()

    def receive(self, text=None, bytes=None, **kwargs):
        pass
