#! ./venv/bin/python 3.7
# -*- coding: utf-8 -*-

"""
handler - функция проверки корректности введенных данных.
На вход принемает text (текст входящего сообщения) и context (dict)
возвращает bool: True - шаг пройден, False - данные не корректны
"""

import re

from generate_ticket import generate_ticket
from models import Registration

re_name = re.compile(r'^[a-zа-яA-ZА-Я]{1}[\w\-\s]{2,29}$')
re_email = re.compile(r'[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+')


def name_handler(text, context):
    if re.match(re_name, text):
        context['name'] = text
        return True
    return False


def email_handler(text, context):
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    return False


def ticket_handler(text, context):
    return generate_ticket(name=context['name'], email=context['email'])


def finish_registration_handler(text, context):
    Registration(user_name=context['name'], email=context['email'])
