# -*- coding: utf-8 -*-
import os
import errno
try:
    import simplejson as json
except ImportError:
    import json
import base64
from Crypto.Cipher import AES


def get_redis_instance():
    from webterminallte.asgi import channel_layer
    return channel_layer._connection_list[0]


class WebsocketAuth(object):

    @property
    def authenticate(self):
        # user auth function to be implement
        if self.ip and self.id:
            conn = get_redis_instance()
            data = conn.get(self.id)
            try:
                data = json.loads(data)
            except:
                return False
            if data and data.get("ip", "") == self.ip:
                return True
            return False

    def haspermission(self, perm):
        # permission auth
        if self.message.user.has_perm(perm):
            return True
        else:
            return False


def mkdir_p(path):
    """
    Pythonic version of "mkdir -p".  Example equivalents::

        >>> mkdir_p('/tmp/test/testing') # Does the same thing as...
        >>> from subprocess import call
        >>> call('mkdir -p /tmp/test/testing')

    .. note:: This doesn't actually call any external commands.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise  # The original exception


class CustomeFloatEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, float):
            return format(obj, '.6f')
        return json.JSONEncoder.encode(self, obj)


class EnDeCrypt(object):

    def __init__(self, key='HOrUmuJ4bCVG6EYu2docoRNNYSdDpJJw'):
        self.key = key

    def add_to_16(self, value):
        while len(value) % 16 != 0:
            value += '\0'
        return str.encode(value)

    def encrypt(self, text):
        aes = AES.new(self.add_to_16(self.key), AES.MODE_ECB)

        encrypt_aes = aes.encrypt(self.add_to_16(text))
        encrypted_text = str(base64.encodebytes(
            encrypt_aes), encoding='utf-8').replace('\n', '')
        return encrypted_text

    def decrypt(self, text):
        aes = AES.new(self.add_to_16(self.key), AES.MODE_ECB)
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
        decrypted_text = str(aes.decrypt(base64_decrypted),
                             encoding='utf-8').replace('\0', '')
        return decrypted_text
