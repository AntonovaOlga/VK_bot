#! ./venv/bin/python3.7
# -*- coding: utf-8 -*-
from pony.orm import db_session
import requests
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
import handlers
import random
from models import UserStates, Registration

try:
    import settings
except Exception as exp:
    print(exp)
    exit("Do cp settings.py.default settings.py and set TOKEN and GROUP_ID")


def log_configure():
    """
    Создание и настройка объекта логирования
    :return: Logger Objects
    """
    log = logging.getLogger("bot")
    log.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler("bot.log", delay=True)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    return log


class Bot:
    """
    Echo bot для vk.com

    Use Python 3.7
    """

    def __init__(self, group_id, token, logger):
        """
        :param group_id: group id из группы в vk
        :param token: секретный токен
        :param logger: Logger Objects
        """
        self.gid = group_id
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.bot_longpoller = VkBotLongPoll(vk=self.vk_session, group_id=self.gid)
        self.api = self.vk_session.get_api()
        self.logger = logger

    def run(self):
        """
        Запуск бота
        """
        for evn in self.bot_longpoller.listen():
            try:
                self.on_event(evn)
            except Exception:
                self.logger.exception("ошибка при обработке события")

    @db_session
    def on_event(self, event):
        """
        Регистрирует пользователь на конференцию, отвечает на вопросы где и когда она пройдет.
        :param event: VkBotMessageEvent
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            self.logger.debug("событие типа %s не обрабатывается", event.type)
            return
        user_id = int(event.object.peer_id)
        text = event.object.text

        state = UserStates.get(user_id=user_id)

        if state is not None:
            self.continue_scenario(user_id=user_id, state=state, text=text)
        else:
            # find intent
            for intent in settings.INTENTS:
                if any(token in text.lower() for token in intent['tokens']):
                    self.logger.debug(f'Обработка intent {intent["name"]}')
                    if intent['answer']:
                        self.send_intent(intent, user_id)
                    else:
                        self.start_scenario(user_id=user_id, scenario_name=intent['scenario'])
                    break
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)
                self.logger.debug(f'Интент не распознан')

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['steps'][scenario['first_step']]
        UserStates(user_id=user_id, scenario_name=scenario_name, step=scenario['first_step'], context={})
        self.send_step(first_step, user_id, context={})

    def continue_scenario(self, user_id, state, text):
        scenario = settings.SCENARIOS[state.scenario_name]
        step = scenario['steps'][state.step]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = scenario['steps'][step['next_step']]
            self.send_step(next_step, user_id, state.context)
            if next_step['next_step']:
                state.step = step['next_step']
            else:
                # finish scenario
                if next_step.get('finish'):
                    finish_handler = getattr(handlers, next_step['finish'])
                    finish_handler(text, state.context)
                self.logger.info(f'Сценарий {state.scenario_name} завершен')
                state.delete()
                db_session()
        else:
            # retry current step
            self.send_step(step, user_id, state.context, on_failure=True)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=str(user_id)
        )
        self.logger.debug(f"Сообщение отправлено {text_to_send}")

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        response = requests.post(url=upload_url, files={'photo': ('ticket.png', image, 'image/png')}).json()
        img_data = self.api.photos.saveMessagesPhoto(**response)
        owner_id = img_data[0]['owner_id']
        media_id = img_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(0, 2 ** 20),
            peer_id=str(user_id)
        )

    def send_step(self, step, user_id, context, on_failure=False):
        text = step.get('text')
        img = step.get('image')
        if on_failure:
            text = step.get('failure_text')
            img = step.get('failure_image')
        if text:
            self.send_text(text.format(**context), user_id)
        if img:
            img_generate = getattr(handlers, img)
            img_to_send = img_generate(text, context)
            self.send_image(img_to_send, user_id)

    def send_intent(self, intent, user_id):
        self.send_text(intent['answer'], user_id)
        if intent.get('answer_image'):
            with open(intent['answer_image'], mode='rb') as f:
                self.send_image(f, user_id)


if __name__ == '__main__':
    log = log_configure()
    bot = Bot(settings.GROUP_ID, settings.TOKEN, log)
    bot.run()
