"""
@author: chuanchao.peng
@date: 2022/1/18 13:46
@file encrypt.py
@desc: 特殊字段需要加密，如用户的身份证、手机号码等信息
"""

from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import AES
from django.conf import settings


def add_to_16(text):
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')


def encrypt(message: str):
    """
    加密信息
    :param message: 待加密的信息
    :return:
    """
    cyper = AES.new(settings.KEY.encode('utf8'), AES.MODE_CBC, settings.IV.encode('utf8'))
    cyper_text = cyper.encrypt(add_to_16(message))
    return b2a_hex(cyper_text).decode()


def decrypt(cyper_message: str):
    """解密"""
    cyper_message = a2b_hex(cyper_message)
    cyper = AES.new(settings.KEY.encode('utf8'), AES.MODE_CBC, settings.IV.encode('utf8'))
    message = cyper.decrypt(cyper_message)
    message = bytes.decode(message).rstrip('\0')
    return message
