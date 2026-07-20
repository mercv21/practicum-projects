"""Пользовательские поля для сериализаторов."""

import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для приёма изображения в формате base64."""

    def to_internal_value(self, data):
        """Преобразует base64-строку в объект файла."""
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                decoded = base64.b64decode(imgstr)
                return ContentFile(decoded, name=f'temp.{ext}')
            except Exception as e:
                raise serializers.ValidationError(
                    f'Некорректный формат base64: {str(e)}'
                )
        return super().to_internal_value(data)
