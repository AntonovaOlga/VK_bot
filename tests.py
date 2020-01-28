from unittest import TestCase
from unittest.mock import Mock, patch, ANY

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType
from chatbot import Bot
import settings
from copy import deepcopy

from generate_ticket import generate_ticket


def test_transaction(func):
    def wrapper(*args, **kwargs):
        with db_session():
            func(*args, **kwargs)
            rollback()

    return wrapper


class Tests(TestCase):
    RAW_EVENT = {
        'type': VkBotEventType.MESSAGE_NEW,
        'object': {
            'date': 1571572216, 'from_id': 26174553, 'id': 21, 'out': 0, 'peer_id': 00000000, 'text': 'test',
            'conversation_message_id': 21, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [],
            'is_hidden': False
        },
        'group_id': 186807662}

    INPUTS = [
        'Вопрос',
        'Привет!',
        'Когда?',
        'Куда приходить?',
        'Зарегистрируй',
        'Иван',
        'fgh@ghj',
        'мой адрес ivan@ivan.iv',
        'спасибо!'
    ]

    EXPECTED_OUTPUT = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.INTENTS[2]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Иван', email='ivan@ivan.iv'),
        settings.INTENTS[3]['answer']
    ]

    @test_transaction
    def test_bot(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock
        logger_mock = Mock('chatbot.logger')
        logger_mock.debug = Mock()
        logger_mock.info = Mock()

        events = []
        for input_text in self.INPUTS:
            event_row = deepcopy(self.RAW_EVENT)
            event_row['object']['text'] = input_text
            events.append(VkBotMessageEvent(raw=event_row))

        longpoller_listen_mock = Mock()
        longpoller_listen_mock.listen = Mock(return_value=events)

        with patch('chatbot.VkBotLongPoll', return_value=longpoller_listen_mock):
            bot = Bot('', '', logger_mock)
            bot.api = api_mock
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUT

    def test_generation_ticket(self):
        avatar_mock = Mock()
        with open('files/template@email.tmp.png', mode='rb') as avatar_file:
            avatar_mock.content = avatar_file.read()
        with patch('requests.get', return_value = avatar_mock):
            ticket = generate_ticket('Name', 'template@email.tmp')
        with open('files/ticket_example.png', mode='rb') as expected_file:
            assert ticket.read() == expected_file.read()
