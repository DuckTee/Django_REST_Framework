import re
from rest_framework.exceptions import ValidationError


class LinkValidator:
    def __init__(self, field=None):
        self.field = field
        # Регулярное выражение для YouTube‑ссылок
        self.youtube_pattern = re.compile(
            r'^(https?://)?'                # http:// или https://
            r'(www\.)?'                     # www.
            r'(youtube\.com|youtu\.be)'    # домен
            r'(/watch\?v=|/embed/|/v/|/)'  # пути
            r'[\w-]{11}'                   # ID видео (11 символов)
            r'(\?|&|$)'                   # конец строки или параметры
        )

    def __call__(self, value):
        if not value:
            return

        # Проверяем соответствие шаблону YouTube
        if not self.youtube_pattern.match(value):
            raise ValidationError(
                'Разрешены только ссылки на YouTube (youtube.com или youtu.be).'
            )

    def __eq__(self, other):
        return isinstance(other, LinkValidator) and self.field == other.field
