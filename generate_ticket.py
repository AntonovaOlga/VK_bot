from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = 'files/OpenSans-Regular.ttf'
TEMPLATE_PATH = 'files/template.png'
FONT_SIZE = 25
BLACK = '#000'
NAME_OFFSET = (345, 190)
EMAIL_OFFSET = (345, 240)
AVATAR_SIZE = 135
AVATAR_OFFSET = (105, 180)


def generate_ticket(name, email):
    try:
        font = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)
        template_img = Image.open(TEMPLATE_PATH)
    except FileNotFoundError:
        raise FileNotFoundError('Не наден файл шрифта или шаблона')

    draw = ImageDraw.Draw(template_img)
    draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
    draw.text(EMAIL_OFFSET, email, font=font, fill=BLACK)

    response = requests.get(f'https://api.adorable.io/avatars/{AVATAR_SIZE}/{email}')
    avatar_file_like = BytesIO(response.content)
    avatar = Image.open(avatar_file_like)
    template_img.paste(avatar, AVATAR_OFFSET)

    tmp_file = BytesIO()
    template_img.save(tmp_file, 'png')
    tmp_file.seek(0)

    return tmp_file


if __name__ == '__main__':
    print(generate_ticket('Name', 'template@email.tmp'))
