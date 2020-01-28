

GROUP_ID = 186807662
TOKEN = "9a81d007fd3a19cff76112bd2f910576106cec4f44d69f4eb393cc2256ae190e6369f75f4b411278f1633"


# DB_CONFIG = dict(
#     provider='postgres',
#     user='fa',
#     password='fa',
#     host='192.168.1.7',
#     database='vk_bot_db'
# )

DB_CONFIG = dict(
    provider='postgres',
    user='olya',
    password='1',
    host='127.0.0.1',
    database='vk_bot_db'
)

INTENTS = [
    {
        'name': 'Приветствие',
        'tokens': ('привет', 'здравств', 'hello', 'hi'),
        'scenario': None,
        'answer': 'Приветствую вас! Меня зовут Бот. '
                  'Я могу сказать когда и где пройдет конференция и зарегистрировать вас.'
    },
    {
        'name': 'Дата проведения',
        'tokens': ('когда', 'сколько', 'дат', 'врем'),
        'scenario': None,
        'answer': 'Конференция будет проходить 14 декабря с 11:00 до 20:00. Регистрация начинается в 09:00'

    },
    {
        'name': 'Место проведения',
        'tokens': ('где', 'место', 'адрес', 'локация', 'добраться', 'метро', 'куда'),
        'scenario': None,
        'answer_image': 'files/map.png',
        'answer': 'Конференция пройдет в павильоне F в Экспофорум по адресу г. Санкт-Петербург Петербургское ш., 64'
    },
    {
        'name': 'До встречи',
        'tokens': ('спасиб', 'пока', 'досвидан'),
        'scenario': None,
        'answer': 'До встречи на конференции'
    },
    {
        'name': 'Регистрация',
        'tokens': ('регистр', 'добав', 'запис', 'участие'),
        'scenario': 'registration',
        'answer': None
    }
]

SCENARIOS = {
    'registration': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Для регистрации введите имя. Оно будет написано на бэйджике.',
                'failure_text': 'Имя должно начинатся с буквы, состоять из 3-30 символов, '
                                'допускается использование дефиса. Повторите попытку.',
                'handler': 'name_handler',
                'next_step': 'step2'
            },

            'step2': {
                'text': 'Введите email. На указанный email будут направлены все данные',
                'failure_text': 'Email указан некорректно. Повторите попытку',
                'handler': 'email_handler',
                'next_step': 'step3'
            },
            'step3': {
                'text': '{name}, спвсибо за регистрацию! Мы отправили билеты а ваш адрес {email}.',
                'image': 'ticket_handler',
                'failure_text': None,
                'handler': None,
                'next_step': None,
                'finish': 'finish_registration_handler'
            }
        }
    }
}

DEFAULT_ANSWER = 'Не знаю как ответить на ваш вопрос. ' \
                 'Могу сказать когда и где пройдет конференция и зарегистрировать вас.'
